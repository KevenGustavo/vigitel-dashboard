import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (caso exista) na raiz do projeto
load_dotenv()

class Config:
    """
    Configurações centralizadas do projeto (ETL e API).
    Carrega as variáveis de ambiente com fallbacks seguros.
    """
    POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "adminpassword")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "vigitel_warehouse")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    @classmethod
    def get_database_url_sync(cls) -> str:
        """Retorna a connection string para o SQLAlchemy (Síncrono/psycopg2) usado pelo ETL."""
        return (
            f"postgresql+psycopg2://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
            f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        )
    
    @classmethod
    def get_database_url_async(cls) -> str:
        """Retorna a connection string para o SQLAlchemy (Assíncrono/asyncpg) usado pela API."""
        return (
            f"postgresql+asyncpg://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
            f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        )

config = Config()
