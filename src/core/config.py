import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
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
            parsed = urlparse(database_url)
            qs = parse_qs(parsed.query)
            # Remove parâmetros incompatíveis com libpq/psycopg2 como channel_binding
            qs.pop("channel_binding", None)
            new_query = urlencode({k: v[0] for k, v in qs.items()})
            cleaned = parsed._replace(scheme="postgresql+psycopg2", query=new_query)
            return urlunparse(cleaned)

        return (
            f"postgresql+psycopg2://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
            f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        )
    
    @classmethod
    def get_database_url_async(cls) -> str:
        """Retorna a connection string para o SQLAlchemy (Assíncrono/asyncpg) usado pela API."""
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            parsed = urlparse(database_url)
            qs = parse_qs(parsed.query)

            # asyncpg aceita apenas parâmetros específicos via URL (ex: ssl).
            # Remove channel_binding, sslmode, etc., que causam TypeError: connect() got unexpected keyword argument
            valid_params = {}
            if "sslmode" in qs:
                mode = qs["sslmode"][0]
                valid_params["ssl"] = "require" if mode in ("require", "verify-ca", "verify-full") else "prefer"
            elif "ssl" in qs:
                valid_params["ssl"] = qs["ssl"][0]

            new_query = urlencode(valid_params)
            cleaned = parsed._replace(scheme="postgresql+asyncpg", query=new_query)
            return urlunparse(cleaned)

        return (
            f"postgresql+asyncpg://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
            f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        )

config = Config()
