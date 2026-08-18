"""
Gold Layer — Modelagem Dimensional (Star Schema) via SQL.

Constrói as dimensões e a tabela Fato diretamente no PostgreSQL,
evitando transferência de dados para o Python.
Inclui criação de índices para otimizar consultas analíticas da API.
"""
import time
import logging

from sqlalchemy import text
from src.etl.database import engine

logger = logging.getLogger(__name__)

# Mapeamento dos nomes de cidade crus (minúsculos sem acento) para os nomes legíveis das 27 capitais
CAPITAIS_MAPEAMENTO = {
    'rio branco': 'Rio Branco', 'maceio': 'Maceió', 'macapa': 'Macapá',
    'manaus': 'Manaus', 'salvador': 'Salvador', 'fortaleza': 'Fortaleza',
    'distrito federal': 'Brasília', 'vitoria': 'Vitória', 'goiania': 'Goiânia',
    'sao luis': 'São Luís', 'cuiaba': 'Cuiabá', 'campo grande': 'Campo Grande',
    'belo horizonte': 'Belo Horizonte', 'belem': 'Belém', 'joao pessoa': 'João Pessoa',
    'curitiba': 'Curitiba', 'recife': 'Recife', 'teresina': 'Teresina',
    'rio de janeiro': 'Rio de Janeiro', 'natal': 'Natal', 'porto alegre': 'Porto Alegre',
    'porto velho': 'Porto Velho', 'boa vista': 'Boa Vista', 'florianopolis': 'Florianópolis',
    'sao paulo': 'São Paulo', 'aracaju': 'Aracaju', 'palmas': 'Palmas',
}


def run():
    """Constrói o Star Schema na camada Gold via SQL."""
    logger.info("Iniciando processamento da camada Gold (Star Schema)...")
    start = time.time()

    with engine.begin() as conn:
        # ── Limpeza prévia ────────────────────────────────────
        for tbl in ['fato_atividade_fisica', 'dim_tempo', 'dim_cidade', 'dim_perfil']:
            conn.execute(text(f"DROP TABLE IF EXISTS gold.{tbl} CASCADE;"))

        # ── 1. Dimensão Tempo ─────────────────────────────────
        conn.execute(text("""
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
        """))
        conn.execute(text("ALTER TABLE gold.dim_tempo ADD PRIMARY KEY (sk_tempo);"))
        logger.info("dim_tempo criada.")

        # ── 2. Dimensão Cidade ────────────────────────────────
        # Insere primeiro com código, depois faz UPDATE com nomes
        conn.execute(text("""
            CREATE TABLE gold.dim_cidade AS
            SELECT
                ROW_NUMBER() OVER (ORDER BY id_cidade)::int AS sk_cidade,
                id_cidade::text AS id_cidade,
                NULL::text AS nome_cidade
            FROM (SELECT DISTINCT id_cidade FROM silver.vigitel_cleansed
                  WHERE id_cidade IS NOT NULL) sub;
        """))
        conn.execute(text("ALTER TABLE gold.dim_cidade ADD PRIMARY KEY (sk_cidade);"))

        # Popula os nomes das capitais
        for nome_cru, nome_formatado in CAPITAIS_MAPEAMENTO.items():
            conn.execute(text(
                "UPDATE gold.dim_cidade SET nome_cidade = :nome_formatado "
                "WHERE id_cidade = :nome_cru"
            ), {"nome_formatado": nome_formatado, "nome_cru": nome_cru})
        logger.info("dim_cidade criada com nomes das capitais.")

        # ── 3. Dimensão Perfil ────────────────────────────────
        conn.execute(text("""
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
        """))
        conn.execute(text("ALTER TABLE gold.dim_perfil ADD PRIMARY KEY (sk_perfil);"))
        logger.info("dim_perfil criada com faixas etárias e de escolaridade.")

        # ── 4. Tabela Fato ────────────────────────────────────
        conn.execute(text("""
            CREATE TABLE gold.fato_atividade_fisica AS
            SELECT
                s.sk_registro,
                dt.sk_tempo,
                dc.sk_cidade,
                dp.sk_perfil,

                -- Peso amostral (epidemiológico)
                s.peso_amostral::numeric AS peso_amostral,

                -- Variáveis brutas relevantes para o dashboard
                s.pratica_exercicio_lazer,
                s.tipo_exercicio_principal,
                s.duracao_minutos_lazer,
                s.deslocamento_trabalho_ativo,
                s.assiste_tv,
                s.horas_sentado_dia,

                -- Indicadores oficiais pré-calculados
                s.ind_af_total,
                s.minutos_lazer_semana,
                s.ind_ativo_lazer,
                s.ind_inativo_lazer,
                s.ind_inativo_total,
                s.ind_ativo_lazer_150min,
                s.ind_ativo_ocupacional,
                s.ind_ativo_transporte,
                s.ind_ativo_domestico,
                s.minutos_desloc_trabalho,
                s.minutos_desloc_escola,
                s.minutos_desloc_dia,
                s.minutos_desloc_semana,
                s.minutos_ocupacional_semana,
                s.minutos_domestico_semana,
                s.ind_af_3dominios_150min,
                s.ind_af_insuficiente,
                s.ind_af_4dominios_150min,
                s.ind_tv_maior_3h,
                s.ind_tela_s_tv_maior_3h,
                s.ind_tela_total_maior_3h,

                -- Desfechos de saúde
                s.ind_hipertensao,
                s.ind_diabetes,
                s.ind_depressao

            FROM silver.vigitel_cleansed s
            LEFT JOIN gold.dim_tempo dt
                ON s.ano_coleta::text = dt.ano_coleta::text
            LEFT JOIN gold.dim_cidade dc
                ON s.id_cidade::text = dc.id_cidade::text
            LEFT JOIN gold.dim_perfil dp
                ON dp.faixa_etaria = CASE
                        WHEN s.idade_anos::numeric < 25 THEN '18-24'
                        WHEN s.idade_anos::numeric < 35 THEN '25-34'
                        WHEN s.idade_anos::numeric < 45 THEN '35-44'
                        WHEN s.idade_anos::numeric < 55 THEN '45-54'
                        WHEN s.idade_anos::numeric < 65 THEN '55-64'
                        ELSE '65+'
                    END
                AND dp.sexo = s.sexo
                AND dp.raca_cor = s.raca_cor
                AND dp.faixa_escolaridade = CASE
                        WHEN s.anos_estudo::numeric BETWEEN 0 AND 8 THEN '0-8 anos'
                        WHEN s.anos_estudo::numeric BETWEEN 9 AND 11 THEN '9-11 anos'
                        WHEN s.anos_estudo::numeric >= 12 THEN '12+ anos'
                        ELSE 'Não informado'
                    END;
        """))
        logger.info("fato_atividade_fisica criada.")

        # ── 5. Índices para performance analítica ─────────────
        conn.execute(text("CREATE INDEX idx_fato_tempo ON gold.fato_atividade_fisica (sk_tempo);"))
        conn.execute(text("CREATE INDEX idx_fato_cidade ON gold.fato_atividade_fisica (sk_cidade);"))
        conn.execute(text("CREATE INDEX idx_fato_perfil ON gold.fato_atividade_fisica (sk_perfil);"))
        logger.info("Índices B-Tree criados nas Foreign Keys da Fato.")

        # Contagem final
        count = conn.execute(text("SELECT count(*) FROM gold.fato_atividade_fisica")).scalar()

    elapsed = time.time() - start
    logger.info("Gold concluída: %d linhas na Fato em %.1fs", count, elapsed)
    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run()
