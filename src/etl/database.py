"""
Módulo de conexão e infraestrutura de banco de dados para o pipeline ETL.

Configura a SQLAlchemy Engine com connection pooling robusto e parâmetros de
sessão do PostgreSQL (work_mem e maintenance_work_mem) para acelerar
operações de junção, ordenação e construção de índices.
"""

from sqlalchemy import create_engine

from src.core.config import config

engine = create_engine(
    config.get_database_url_sync(),
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"options": "-c work_mem=128MB -c maintenance_work_mem=256MB"},
)
