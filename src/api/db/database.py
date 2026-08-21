from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.config import config

# Cria a engine assíncrona usando asyncpg para o FastAPI
engine = create_async_engine(
    config.get_database_url_async(), 
    echo=False,
    connect_args={"server_settings": {"work_mem": "64MB"}}
)

# Session factory configurado para requisições assíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db():
    """
    Gera a sessão assíncrona do banco de dados e garante seu fechamento após o uso.
    A ser utilizada como Dependency Injection nas rotas do FastAPI.
    """
    async with AsyncSessionLocal() as session:
        yield session
