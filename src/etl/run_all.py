"""
Orquestrador do pipeline ETL (Bronze → Silver → Gold).

Executa as três camadas em sequência, com logging estruturado
e medição de tempo total.
"""
import time
import logging

from src.etl.jobs import load_bronze, process_silver, build_gold

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("pipeline")


def run_pipeline():
    """Executa o pipeline completo."""
    logger.info("=" * 60)
    logger.info("INICIANDO PIPELINE DE DADOS VIGITEL")
    logger.info("=" * 60)

    start = time.time()

    bronze_count = load_bronze.run()
    logger.info("-" * 60)

    silver_count = process_silver.run()
    logger.info("-" * 60)

    gold_count = build_gold.run()
    logger.info("-" * 60)

    elapsed = time.time() - start
    logger.info("PIPELINE CONCLUÍDO — Bronze: %d | Silver: %d | Gold: %d | Tempo: %.1fs",
                bronze_count, silver_count, gold_count, elapsed)


if __name__ == "__main__":
    run_pipeline()
