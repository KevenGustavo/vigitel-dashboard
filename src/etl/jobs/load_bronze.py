"""
Bronze Layer — Ingestão do CSV bruto para o PostgreSQL.

Lê o arquivo CSV do VIGITEL em chunks para controlar o consumo de memória
(o arquivo completo tem ~1GB) e grava diretamente na tabela bronze.vigitel_raw.
Nenhuma transformação é aplicada nesta camada.
"""
import pandas as pd
import time
import logging

from src.etl.database import engine
from src.etl.schema import get_csv_columns

logger = logging.getLogger(__name__)

CSV_PATH = "data/raw/vigitel-2006-2024-peso-rake.csv"
ENCODING = "latin-1"
CHUNK_SIZE = 50_000


def run():
    """Executa a ingestão incremental do CSV para a camada Bronze."""
    logger.info("Iniciando ingestão da camada Bronze...")
    start = time.time()

    columns = get_csv_columns()
    logger.info("Colunas selecionadas do contrato: %d", len(columns))

    reader = pd.read_csv(
        CSV_PATH,
        encoding=ENCODING,
        usecols=columns,
        chunksize=CHUNK_SIZE,
        low_memory=False,
        dtype=str,
    )

    total_rows = 0
    for i, chunk in enumerate(reader):
        mode = "replace" if i == 0 else "append"
        chunk.to_sql(
            name="vigitel_raw",
            con=engine,
            schema="bronze",
            if_exists=mode,
            index=False,
            method="multi",
            chunksize=500,  # 500 linhas x 74 colunas = 37.000 parâmetros (< limite de 65.535 do PG)
        )
        total_rows += len(chunk)
        logger.info("  Chunk %d gravado (%d linhas acumuladas)", i + 1, total_rows)

    elapsed = time.time() - start
    rate = total_rows / elapsed if elapsed > 0 else 0
    logger.info("Bronze concluída: %d linhas em %.1fs (%.0f linhas/s)", total_rows, elapsed, rate)
    return total_rows


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run()
