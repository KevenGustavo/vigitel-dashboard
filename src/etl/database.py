from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.etl.config import config

# Cria a engine central com o pooling padrão do SQLAlchemy
engine = create_engine(config.get_database_url(), echo=False)

# Session factory configurado
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Gera a sessão do banco de dados e garante seu fechamento após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
