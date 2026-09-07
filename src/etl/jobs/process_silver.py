"""
Silver Layer — Limpeza e padronização via SQL de passagem única (Single-Pass ELT).

Todas as transformações, substituição de códigos mágicos e mapeamentos semânticos
são executadas diretamente no PostgreSQL em uma única operação CREATE TABLE AS SELECT.
Isso evita a geração de dezenas de milhões de tuplas mortas (table bloat) decorrentes
de comandos UPDATE repetidos sobre 833.000+ linhas, reduzindo o tempo de processamento
de minutos para poucos segundos.
"""

import time
import logging

from sqlalchemy import text
from src.etl.database import engine
from src.etl.schema import COLUMN_MAP, CONTINUOUS_COLUMNS, MAGIC_NULL_CODES

logger = logging.getLogger(__name__)

# Mapeamento dos nomes de cidade crus para os nomes oficiais das 27 capitais brasileiras
CAPITAIS_MAPEAMENTO = {
    "rio branco": "Rio Branco",
    "maceio": "Maceió",
    "macapa": "Macapá",
    "manaus": "Manaus",
    "salvador": "Salvador",
    "fortaleza": "Fortaleza",
    "distrito federal": "Brasília",
    "vitoria": "Vitória",
    "goiania": "Goiânia",
    "sao luis": "São Luís",
    "cuiaba": "Cuiabá",
    "campo grande": "Campo Grande",
    "belo horizonte": "Belo Horizonte",
    "belem": "Belém",
    "joao pessoa": "João Pessoa",
    "curitiba": "Curitiba",
    "recife": "Recife",
    "teresina": "Teresina",
    "rio de janeiro": "Rio de Janeiro",
    "natal": "Natal",
    "porto alegre": "Porto Alegre",
    "porto velho": "Porto Velho",
    "boa vista": "Boa Vista",
    "florianopolis": "Florianópolis",
    "sao paulo": "São Paulo",
    "aracaju": "Aracaju",
    "palmas": "Palmas",
}


def _build_projection_sql() -> str:
    """
    Gera a cláusula SELECT projetando todas as colunas do contrato com
    limpeza de códigos mágicos e padronização semântica em passagem única.
    """
    cases_cidades = "\n            ".join(
        [f"WHEN '{k}' THEN '{v}'" for k, v in CAPITAIS_MAPEAMENTO.items()]
    )

    # Códigos mágicos para a cláusula IN (...) do PostgreSQL
    magic_codes_sql = ", ".join(repr(str(c)) for c in sorted(list(MAGIC_NULL_CODES), key=str))

    projections = ["gen_random_uuid()::text AS sk_registro"]

    for original, renamed in COLUMN_MAP.items():
        if renamed in CONTINUOUS_COLUMNS:
            # Colunas contínuas não sofrem eliminação de códigos mágicos
            projections.append(f'"{original}" AS "{renamed}"')
        elif renamed == "nome_cidade":
            projections.append(f"""CASE LOWER(TRIM("{original}"))
            {cases_cidades}
            ELSE INITCAP(TRIM("{original}"))
        END AS "{renamed}" """)
        elif renamed == "sexo":
            projections.append(f"""CASE
            WHEN TRIM("{original}") IN ({magic_codes_sql}) THEN NULL
            WHEN "{original}" IS NULL THEN NULL
            ELSE INITCAP(TRIM("{original}"))
        END AS "{renamed}" """)
        elif renamed == "raca_cor":
            projections.append(f"""CASE
            WHEN TRIM("{original}") IN ({magic_codes_sql}, 'não sabe') THEN NULL
            WHEN TRIM("{original}") = '80' THEN 'Outros'
            WHEN LOWER(TRIM("{original}")) = 'vermelha' THEN 'Indígena'
            WHEN LOWER(TRIM("{original}")) IN ('parda', 'parda/morena') THEN 'Parda'
            WHEN "{original}" IS NULL THEN NULL
            ELSE INITCAP(TRIM("{original}"))
        END AS "{renamed}" """)
        elif renamed == "deslocamento_trabalho_ativo":
            projections.append(f"""CASE
            WHEN TRIM("{original}") IN ({magic_codes_sql}) THEN NULL
            WHEN TRIM("{original}") = '3' THEN 'não trabalha fora'
            ELSE "{original}"
        END AS "{renamed}" """)
        elif renamed == "tipo_exercicio_principal":
            projections.append(f"""CASE
            WHEN TRIM("{original}") IN ({magic_codes_sql}) THEN NULL
            WHEN TRIM("{original}") = '17' THEN 'outros'
            ELSE "{original}"
        END AS "{renamed}" """)
        elif renamed == "duracao_minutos_lazer":
            projections.append(f"""CASE
            WHEN TRIM("{original}") IN ({magic_codes_sql}) THEN NULL
            WHEN TRIM("{original}") = '7' THEN '40 a 44'
            ELSE "{original}"
        END AS "{renamed}" """)
        else:
            # Demais colunas categóricas: substitui códigos mágicos por NULL
            projections.append(f"""CASE
            WHEN TRIM("{original}") IN ({magic_codes_sql}) THEN NULL
            ELSE "{original}"
        END AS "{renamed}" """)

    return ",\n        ".join(projections)


def run() -> int:
    """Executa a transformação da camada Silver em passagem única (Single-Pass ELT)."""
    logger.info("Iniciando processamento da camada Silver (Single-Pass ELT)...")
    start = time.time()

    select_clause = _build_projection_sql()

    with engine.begin() as conn:
        # 1. Dropar tabela anterior
        conn.execute(text("DROP TABLE IF EXISTS silver.vigitel_cleansed CASCADE;"))
        logger.info("Tabela silver.vigitel_cleansed anterior removida.")

        # 2. Criar a nova tabela Silver já limpa e padronizada em único passo
        create_sql = f"""
        CREATE TABLE silver.vigitel_cleansed AS
        SELECT
            {select_clause}
        FROM bronze.vigitel_raw;
        """
        conn.execute(text(create_sql))
        logger.info("Tabela silver.vigitel_cleansed criada via Single-Pass ELT.")

        # 3. Contar registros
        count = conn.execute(text("SELECT count(*) FROM silver.vigitel_cleansed")).scalar()

    elapsed = time.time() - start
    rate = count / elapsed if elapsed > 0 else 0
    logger.info("Silver concluída: %d linhas em %.2fs (%.0f linhas/s)", count, elapsed, rate)
    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run()
