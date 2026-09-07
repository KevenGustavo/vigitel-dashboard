from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.config import config

# Cria a engine assíncrona usando asyncpg com pool de alta resiliência para produção
engine = create_async_engine(
    config.get_database_url_async(),
    echo=False,
    pool_pre_ping=True,
    pool_size=config.DB_POOL_SIZE,
    max_overflow=config.DB_MAX_OVERFLOW,
    pool_recycle=config.DB_POOL_RECYCLE,
    connect_args={"server_settings": {"work_mem": "64MB"}},
)

# Session factory configurado para requisições assíncronas (compatível com SQLAlchemy 2.0)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_db():
    """
    Gera a sessão assíncrona do banco de dados e garante seu fechamento após o uso.
    A ser utilizada como Dependency Injection nas rotas do FastAPI.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def dispose_engine() -> None:
    """Fecha todas as conexões ativas no pool do SQLAlchemy de forma graciosa."""
    await engine.dispose()
