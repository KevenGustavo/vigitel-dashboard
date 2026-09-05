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

    # Configurações do Pool de Conexões assíncronas do PostgreSQL (API)
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))

    # Configurações de CORS
    CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()]

    @classmethod
    def get_database_url_sync(cls) -> str:
        """Retorna a connection string para o SQLAlchemy (Síncrono/psycopg2) usado pelo ETL."""
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            # Compatibilidade com formatos comuns de PaaS (postgres:// -> postgresql+psycopg2://)
            if database_url.startswith("postgres://"):
                return database_url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif database_url.startswith("postgresql://") and not database_url.startswith("postgresql+"):
                return database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return database_url

        return (
            f"postgresql+psycopg2://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
            f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        )
    
    @classmethod
    def get_database_url_async(cls) -> str:
        """Retorna a connection string para o SQLAlchemy (Assíncrono/asyncpg) usado pela API."""
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            # Normaliza protocolo para asyncpg
            if database_url.startswith("postgres://"):
                url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif database_url.startswith("postgresql://") and not database_url.startswith("postgresql+"):
                url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            else:
                url = database_url
            
            # asyncpg utiliza ?ssl=require em vez de ?sslmode=require
            if "sslmode=" in url:
                url = url.replace("sslmode=require", "ssl=require").replace("sslmode=prefer", "ssl=prefer")
            return url

        return (
            f"postgresql+asyncpg://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
            f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        )

config = Config()
