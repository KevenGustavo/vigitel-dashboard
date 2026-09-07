"""
Orquestrador do pipeline ETL (Bronze → Silver → Gold).

Executa as três camadas em sequência, com logging estruturado,
medição precisa de tempo por camada e tratamento robusto de erros
com códigos de saída UNIX para integração contínua (CI/CD) e cron jobs.
"""

import sys
import time
import logging

from src.etl.jobs import load_bronze, process_silver, build_gold

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("pipeline")


def run_pipeline() -> None:
    """Executa o pipeline completo (Bronze → Silver → Gold) com métricas e tratamento de exceção."""
    logger.info("=" * 65)
    logger.info("INICIANDO PIPELINE DE ENGENHARIA DE DADOS VIGITEL")
    logger.info("=" * 65)

    pipeline_start = time.time()

    try:
        # Camada Bronze (Ingestão CSV)
        t0 = time.time()
        bronze_count = load_bronze.run()
        t_bronze = time.time() - t0
        logger.info("-" * 65)

        # Camada Silver (Limpeza & Padronização Single-Pass)
        t0 = time.time()
        silver_count = process_silver.run()
        t_silver = time.time() - t0
        logger.info("-" * 65)

        # Camada Gold (Modelagem Dimensional Star Schema)
        t0 = time.time()
        gold_count = build_gold.run()
        t_gold = time.time() - t0
        logger.info("-" * 65)

        total_elapsed = time.time() - pipeline_start

        logger.info("=" * 65)
        logger.info("PIPELINE CONCLUÍDO COM SUCESSO!")
        logger.info("  • Bronze: %d linhas (%.1fs)", bronze_count, t_bronze)
        logger.info("  • Silver: %d linhas (%.1fs)", silver_count, t_silver)
        logger.info("  • Gold:   %d linhas (%.1fs)", gold_count, t_gold)
        logger.info("  • Tempo Total: %.1fs", total_elapsed)
        logger.info("=" * 65)

    except Exception as exc:
        logger.critical("FALHA CRÍTICA NO PIPELINE ETL: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
