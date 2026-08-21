"""
Silver Layer — Limpeza e padronização via SQL.

Todas as transformações são executadas diretamente no PostgreSQL,
eliminando a transferência de dados pelo driver Python.
Operações realizadas:
  1. Renomear colunas (De-Para do contrato)
  2. Gerar Surrogate Key (UUID)
  3. Limpar códigos mágicos (777, 888, 999) apenas em colunas categóricas
"""
import time
import logging

from sqlalchemy import text
from src.etl.database import engine
from src.etl.schema import COLUMN_MAP, CONTINUOUS_COLUMNS, MAGIC_NULL_CODES

logger = logging.getLogger(__name__)


def _build_rename_sql():
    """Gera a cláusula SELECT com alias para cada coluna do contrato."""
    selects = []
    for original, renamed in COLUMN_MAP.items():
        # Aspas duplas para nomes com caracteres especiais
        selects.append(f'"{original}" AS "{renamed}"')
    return ",\n        ".join(selects)


def _build_null_cleanup_sql():
    """
    Gera UPDATE statements para substituir códigos mágicos por NULL,
    aplicando apenas às colunas categóricas (excluindo contínuas).
    """
    statements = []
    categorical_cols = [v for v in COLUMN_MAP.values() if v not in CONTINUOUS_COLUMNS]

    # Códigos numéricos
    numeric_codes = [c for c in MAGIC_NULL_CODES if isinstance(c, int)]
    # Códigos textuais
    text_codes = [c for c in MAGIC_NULL_CODES if isinstance(c, str)]

    for col in categorical_cols:
        conditions = []
        if numeric_codes:
            nums = ", ".join(str(c) for c in numeric_codes)
            conditions.append(f'"{col}"::text IN ({", ".join(repr(str(c)) for c in numeric_codes)})')
        if text_codes:
            conditions.append(f'"{col}"::text IN ({", ".join(repr(c) for c in text_codes)})')

        if conditions:
            where = " OR ".join(conditions)
            statements.append(
                f'UPDATE silver.vigitel_cleansed SET "{col}" = NULL WHERE {where};'
            )
    return "\n".join(statements)


def run():
    """Executa a transformação Silver inteiramente no PostgreSQL."""
    logger.info("Iniciando processamento da camada Silver (SQL)...")
    start = time.time()

    rename_clause = _build_rename_sql()

    with engine.begin() as conn:
        # 1. Dropar tabela anterior (overwrite)
        conn.execute(text("DROP TABLE IF EXISTS silver.vigitel_cleansed CASCADE;"))
        logger.info("Tabela anterior removida.")

        # 2. Criar a tabela Silver a partir da Bronze com renomeação + UUID
        create_sql = f"""
        CREATE TABLE silver.vigitel_cleansed AS
        SELECT
            gen_random_uuid()::text AS sk_registro,
            {rename_clause}
        FROM bronze.vigitel_raw;
        """
        conn.execute(text(create_sql))
        logger.info("Tabela silver.vigitel_cleansed criada com colunas renomeadas e UUID.")

        # 3. Limpeza seletiva de códigos mágicos (apenas categóricas)
        cleanup_sql = _build_null_cleanup_sql()
        if cleanup_sql:
            conn.execute(text(cleanup_sql))
            logger.info("Códigos mágicos substituídos por NULL nas colunas categóricas.")

        # 4. Limpeza semântica específica do domínio VIGITEL
        #    Trata valores residuais que escaparam da tradução automática do STATA
        semantic_cleanup = """
            -- Trailing spaces em colunas text (ex: 'goiania ' → 'goiania')
            UPDATE silver.vigitel_cleansed SET id_cidade = TRIM(id_cidade)
                WHERE id_cidade != TRIM(id_cidade);

            -- raca_cor: código '80' = 'outros' no dicionário VIGITEL
            UPDATE silver.vigitel_cleansed SET raca_cor = 'outros'
                WHERE raca_cor = '80';

            -- raca_cor: 'não sabe' não é classificação demográfica utilizável → NULL
            UPDATE silver.vigitel_cleansed SET raca_cor = NULL
                WHERE raca_cor = 'não sabe';

            -- deslocamento_trabalho_ativo: '3' = 'não trabalha fora de casa' no dicionário
            UPDATE silver.vigitel_cleansed SET deslocamento_trabalho_ativo = 'não trabalha fora'
                WHERE deslocamento_trabalho_ativo = '3';

            -- tipo_exercicio_principal: '17' = código numérico residual → 'outros'
            UPDATE silver.vigitel_cleansed SET tipo_exercicio_principal = 'outros'
                WHERE tipo_exercicio_principal = '17';

            -- duracao_minutos_lazer: '7' = '40 a 44' minutos no dicionário VIGITEL (q46)
            UPDATE silver.vigitel_cleansed SET duracao_minutos_lazer = '40 a 44'
                WHERE duracao_minutos_lazer = '7';
        """
        conn.execute(text(semantic_cleanup))
        logger.info("Limpeza semântica concluída (trailing spaces, códigos residuais traduzidos).")

        # 5. Contar registros
        count = conn.execute(text("SELECT count(*) FROM silver.vigitel_cleansed")).scalar()

    elapsed = time.time() - start
    logger.info("Silver concluída: %d linhas em %.1fs", count, elapsed)
    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run()
