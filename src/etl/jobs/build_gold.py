"""
Gold Layer — Modelagem Dimensional (Star Schema) via SQL.

Constrói as tabelas de dimensão e a tabela Fato diretamente no PostgreSQL,
garantindo:
  1. Integridade referencial plena (FKs explícitas e NULL-safety via IS NOT DISTINCT FROM)
  2. Tipagem eficiente (BOOLEAN, SMALLINT, NUMERIC)
  3. Indexação B-Tree simples e composta cobrindo os padrões de consulta da API
  4. Organização física em disco (CLUSTER por tempo) e atualização do otimizador (ANALYZE)
"""

import time
import logging

from sqlalchemy import text
from src.etl.database import engine

logger = logging.getLogger(__name__)


def run() -> int:
    """Constrói o Star Schema na camada Gold via SQL com integridade referencial e índices."""
    logger.info("Iniciando processamento da camada Gold (Star Schema)...")
    start = time.time()

    with engine.begin() as conn:
        # ── Limpeza prévia de tabelas e constraints ───────────
        for tbl in ["fato_atividade_fisica", "dim_tempo", "dim_cidade", "dim_perfil"]:
            conn.execute(text(f"DROP TABLE IF EXISTS gold.{tbl} CASCADE;"))

        # ── 1. Dimensão Tempo ─────────────────────────────────
        conn.execute(
            text("""
            CREATE TABLE gold.dim_tempo AS
            SELECT
                ROW_NUMBER() OVER (ORDER BY ano_coleta)::int AS sk_tempo,
                ano_coleta::int AS ano_coleta,
                CASE
                    WHEN ano_coleta::int BETWEEN 2006 AND 2009 THEN '2006-2009'
                    WHEN ano_coleta::int BETWEEN 2010 AND 2014 THEN '2010-2014'
                    WHEN ano_coleta::int BETWEEN 2015 AND 2019 THEN '2015-2019'
                    WHEN ano_coleta::int >= 2020 THEN '2020+'
                END AS periodo
            FROM (SELECT DISTINCT ano_coleta FROM silver.vigitel_cleansed
                  WHERE ano_coleta IS NOT NULL) sub;
        """)
        )
        conn.execute(text("ALTER TABLE gold.dim_tempo ADD PRIMARY KEY (sk_tempo);"))
        conn.execute(text("CREATE INDEX idx_dim_tempo_ano ON gold.dim_tempo (ano_coleta);"))
        logger.info("dim_tempo criada com PK e índice de busca temporal.")

        # ── 2. Dimensão Cidade ────────────────────────────────
        conn.execute(
            text("""
            CREATE TABLE gold.dim_cidade AS
            SELECT
                ROW_NUMBER() OVER (ORDER BY nome_cidade)::int AS sk_cidade,
                nome_cidade::text AS nome_cidade
            FROM (SELECT DISTINCT nome_cidade FROM silver.vigitel_cleansed
                  WHERE nome_cidade IS NOT NULL) sub;
        """)
        )
        conn.execute(text("ALTER TABLE gold.dim_cidade ADD PRIMARY KEY (sk_cidade);"))
        conn.execute(text("CREATE INDEX idx_dim_cidade_nome ON gold.dim_cidade (nome_cidade);"))
        logger.info("dim_cidade criada com PK e índice de busca por capital.")

        # ── 3. Dimensão Perfil ────────────────────────────────
        conn.execute(
            text("""
            CREATE TABLE gold.dim_perfil AS
            SELECT
                ROW_NUMBER() OVER (ORDER BY faixa_etaria, sexo, raca_cor, faixa_escolaridade)::int AS sk_perfil,
                faixa_etaria,
                sexo,
                raca_cor,
                faixa_escolaridade
            FROM (
                SELECT DISTINCT
                    CASE
                        WHEN idade_anos::numeric < 25 THEN '18-24'
                        WHEN idade_anos::numeric < 35 THEN '25-34'
                        WHEN idade_anos::numeric < 45 THEN '35-44'
                        WHEN idade_anos::numeric < 55 THEN '45-54'
                        WHEN idade_anos::numeric < 65 THEN '55-64'
                        ELSE '65+'
                    END AS faixa_etaria,
                    sexo,
                    raca_cor,
                    CASE
                        WHEN anos_estudo::numeric BETWEEN 0 AND 8 THEN '0-8 anos'
                        WHEN anos_estudo::numeric BETWEEN 9 AND 11 THEN '9-11 anos'
                        WHEN anos_estudo::numeric >= 12 THEN '12+ anos'
                        ELSE 'Não informado'
                    END AS faixa_escolaridade
                FROM silver.vigitel_cleansed
                WHERE sexo IS NOT NULL
            ) sub;
        """)
        )
        conn.execute(text("ALTER TABLE gold.dim_perfil ADD PRIMARY KEY (sk_perfil);"))
        conn.execute(
            text("""
            CREATE UNIQUE INDEX idx_dim_perfil_lookup
            ON gold.dim_perfil (faixa_etaria, sexo, raca_cor, faixa_escolaridade)
            NULLS NOT DISTINCT;
        """)
        )
        logger.info("dim_perfil criada com PK e índice único composto.")

        # ── 4. Tabela Fato ────────────────────────────────────
        # Tipagem otimizada: BOOLEAN (1 byte), SMALLINT (2 bytes), NUMERIC para métricas
        # NULL-Safety com IS NOT DISTINCT FROM em dimensões com valores nulos (ex: raca_cor)
        conn.execute(
            text("""
            CREATE TABLE gold.fato_atividade_fisica AS
            SELECT
                s.sk_registro,
                dt.sk_tempo,
                dc.sk_cidade,
                dp.sk_perfil,

                -- Peso amostral (epidemiológico) → NUMERIC
                s.peso_amostral::numeric AS peso_amostral,

                -- Variáveis brutas categóricas → TEXT
                s.tipo_exercicio_principal,
                s.duracao_minutos_lazer,
                s.deslocamento_trabalho_ativo,
                s.horas_sentado_dia,

                -- Variáveis brutas Sim/Não convertidas para BOOLEAN
                CASE WHEN s.pratica_exercicio_lazer = 'sim' THEN TRUE
                     WHEN s.pratica_exercicio_lazer = 'não' THEN FALSE
                     ELSE NULL END::boolean AS pratica_exercicio_lazer,

                CASE WHEN s.assiste_tv = 'sim' THEN TRUE
                     WHEN s.assiste_tv = 'não' THEN FALSE
                     ELSE NULL END::boolean AS assiste_tv,

                -- Indicador de nível de AF (0, 1, 2) → SMALLINT
                s.ind_af_total::smallint AS ind_af_total,

                -- Contínuos de minutos → NUMERIC
                s.minutos_lazer_semana::numeric AS minutos_lazer_semana,
                s.minutos_desloc_trabalho::numeric AS minutos_desloc_trabalho,
                s.minutos_desloc_escola::numeric AS minutos_desloc_escola,
                s.minutos_desloc_dia::numeric AS minutos_desloc_dia,
                s.minutos_desloc_semana::numeric AS minutos_desloc_semana,
                s.minutos_ocupacional_semana::numeric AS minutos_ocupacional_semana,
                s.minutos_domestico_semana::numeric AS minutos_domestico_semana,

                -- Indicadores Sim/Não → BOOLEAN
                CASE WHEN s.ind_inativo_lazer = 'Sim' THEN TRUE
                     WHEN s.ind_inativo_lazer = 'Nao' THEN FALSE
                     ELSE NULL END::boolean AS ind_inativo_lazer,

                CASE WHEN s.ind_inativo_total = 'Sim' THEN TRUE
                     WHEN s.ind_inativo_total = 'Nao' THEN FALSE
                     ELSE NULL END::boolean AS ind_inativo_total,

                CASE WHEN s.ind_ativo_lazer_150min = 'Sim' THEN TRUE
                     WHEN s.ind_ativo_lazer_150min = 'Nao' THEN FALSE
                     ELSE NULL END::boolean AS ind_ativo_lazer_150min,

                CASE WHEN s.ind_af_3dominios_150min = 'Sim' THEN TRUE
                     WHEN s.ind_af_3dominios_150min = 'Nao' THEN FALSE
                     ELSE NULL END::boolean AS ind_af_3dominios_150min,

                CASE WHEN s.ind_af_insuficiente = 'Sim' THEN TRUE
                     WHEN s.ind_af_insuficiente = 'Nao' THEN FALSE
                     ELSE NULL END::boolean AS ind_af_insuficiente,

                CASE WHEN s.ind_af_4dominios_150min = 'Sim' THEN TRUE
                     WHEN s.ind_af_4dominios_150min = 'Nao' THEN FALSE
                     ELSE NULL END::boolean AS ind_af_4dominios_150min,

                CASE WHEN s.ind_tv_maior_3h = 'Sim' THEN TRUE
                     WHEN s.ind_tv_maior_3h = 'Nao' THEN FALSE
                     ELSE NULL END::boolean AS ind_tv_maior_3h,

                CASE WHEN s.ind_tela_s_tv_maior_3h = 'Sim' THEN TRUE
                     WHEN s.ind_tela_s_tv_maior_3h = 'Nao' THEN FALSE
                     ELSE NULL END::boolean AS ind_tela_s_tv_maior_3h,

                CASE WHEN s.ind_tela_total_maior_3h = 'Sim' THEN TRUE
                     WHEN s.ind_tela_total_maior_3h = 'Nao' THEN FALSE
                     ELSE NULL END::boolean AS ind_tela_total_maior_3h,

                CASE WHEN s.ind_hipertensao = 'Sim' THEN TRUE
                     WHEN s.ind_hipertensao = 'Nao' THEN FALSE
                     ELSE NULL END::boolean AS ind_hipertensao,

                CASE WHEN s.ind_diabetes = 'Sim' THEN TRUE
                     WHEN s.ind_diabetes = 'Nao' THEN FALSE
                     ELSE NULL END::boolean AS ind_diabetes,

                CASE WHEN s.ind_depressao = 'Sim' THEN TRUE
                     WHEN s.ind_depressao = 'Nao' THEN FALSE
                     ELSE NULL END::boolean AS ind_depressao,

                -- Desfechos de Saúde Calculados (IMC) → BOOLEAN
                -- IMC = peso_kg / (altura_m)^2
                ((s.peso_kg_imputado::numeric) /
                 POWER((NULLIF(s.altura_cm_imputado::numeric, 0) / 100.0), 2) >= 25)::boolean AS ind_excesso_peso,

                ((s.peso_kg_imputado::numeric) /
                 POWER((NULLIF(s.altura_cm_imputado::numeric, 0) / 100.0), 2) >= 30)::boolean AS ind_obesidade,

                -- Indicadores 0/1 → BOOLEAN
                (s.ind_ativo_ocupacional = '1')::boolean AS ind_ativo_ocupacional,
                (s.ind_ativo_transporte = '1')::boolean AS ind_ativo_transporte,
                (s.ind_ativo_domestico = '1')::boolean AS ind_ativo_domestico,

                -- Indicador Ativo/Inativo → BOOLEAN
                CASE WHEN s.ind_ativo_lazer = 'Ativo' THEN TRUE
                     WHEN s.ind_ativo_lazer = 'Inativo/Ins' THEN FALSE
                     ELSE NULL END::boolean AS ind_ativo_lazer

            FROM silver.vigitel_cleansed s
            LEFT JOIN gold.dim_tempo dt
                ON s.ano_coleta::text = dt.ano_coleta::text
            LEFT JOIN gold.dim_cidade dc
                ON s.nome_cidade::text = dc.nome_cidade::text
            LEFT JOIN gold.dim_perfil dp
                ON dp.faixa_etaria = CASE
                        WHEN s.idade_anos::numeric < 25 THEN '18-24'
                        WHEN s.idade_anos::numeric < 35 THEN '25-34'
                        WHEN s.idade_anos::numeric < 45 THEN '35-44'
                        WHEN s.idade_anos::numeric < 55 THEN '45-54'
                        WHEN s.idade_anos::numeric < 65 THEN '55-64'
                        ELSE '65+'
                    END
                AND dp.sexo IS NOT DISTINCT FROM s.sexo
                AND dp.raca_cor IS NOT DISTINCT FROM s.raca_cor
                AND dp.faixa_escolaridade = CASE
                        WHEN s.anos_estudo::numeric BETWEEN 0 AND 8 THEN '0-8 anos'
                        WHEN s.anos_estudo::numeric BETWEEN 9 AND 11 THEN '9-11 anos'
                        WHEN s.anos_estudo::numeric >= 12 THEN '12+ anos'
                        ELSE 'Não informado'
                    END;
        """)
        )
        logger.info("fato_atividade_fisica criada com junção segura (NULL-safe).")

        # ── 5. Restrições de Integridade (PK e FKs) ───────────
        conn.execute(text("ALTER TABLE gold.fato_atividade_fisica ADD PRIMARY KEY (sk_registro);"))
        conn.execute(
            text("""
            ALTER TABLE gold.fato_atividade_fisica
            ADD CONSTRAINT fk_fato_tempo FOREIGN KEY (sk_tempo) REFERENCES gold.dim_tempo (sk_tempo),
            ADD CONSTRAINT fk_fato_cidade FOREIGN KEY (sk_cidade) REFERENCES gold.dim_cidade (sk_cidade),
            ADD CONSTRAINT fk_fato_perfil FOREIGN KEY (sk_perfil) REFERENCES gold.dim_perfil (sk_perfil);
        """)
        )
        logger.info("Chave Primária e Chaves Estrangeiras adicionadas à Fato.")

        # ── 6. Índices para performance analítica do Dashboard ──
        conn.execute(text("CREATE INDEX idx_fato_tempo ON gold.fato_atividade_fisica (sk_tempo);"))
        conn.execute(
            text("CREATE INDEX idx_fato_cidade ON gold.fato_atividade_fisica (sk_cidade);")
        )
        conn.execute(
            text("CREATE INDEX idx_fato_perfil ON gold.fato_atividade_fisica (sk_perfil);")
        )
        conn.execute(
            text(
                "CREATE INDEX idx_fato_cidade_perfil ON gold.fato_atividade_fisica (sk_cidade, sk_perfil);"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX idx_fato_tempo_cidade_perfil ON gold.fato_atividade_fisica (sk_tempo, sk_cidade, sk_perfil);"
            )
        )
        logger.info("Índices B-Tree simples e compostos criados nas FKs da Fato.")

        # ── 7. Otimização física (CLUSTER) e estatísticas (ANALYZE) ──
        conn.execute(text("CLUSTER gold.fato_atividade_fisica USING idx_fato_tempo;"))
        logger.info("Tabela Fato organizada fisicamente no disco por tempo (CLUSTER).")

        conn.execute(text("ANALYZE gold.dim_tempo;"))
        conn.execute(text("ANALYZE gold.dim_cidade;"))
        conn.execute(text("ANALYZE gold.dim_perfil;"))
        conn.execute(text("ANALYZE gold.fato_atividade_fisica;"))
        logger.info("Estatísticas do otimizador PostgreSQL atualizadas (ANALYZE).")

        # Contagem final
        count = conn.execute(text("SELECT count(*) FROM gold.fato_atividade_fisica")).scalar()

    elapsed = time.time() - start
    rate = count / elapsed if elapsed > 0 else 0
    logger.info("Gold concluída: %d linhas na Fato em %.2fs (%.0f linhas/s)", count, elapsed, rate)
    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run()
