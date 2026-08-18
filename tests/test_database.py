"""
Testes de infraestrutura: conexão com o banco e existência dos schemas.
"""
import pytest
from sqlalchemy import text
from src.etl.database import engine


def test_database_connection():
    """Verifica se a conexão com o PostgreSQL está funcional."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_schemas_exist():
    """Verifica se o init.sql criou corretamente os schemas da arquitetura Medalhão."""
    with engine.connect() as conn:
        query = text(
            "SELECT schema_name FROM information_schema.schemata "
            "WHERE schema_name IN ('bronze', 'silver', 'gold')"
        )
        schemas = {row[0] for row in conn.execute(query).fetchall()}

    assert 'bronze' in schemas, "Schema bronze não encontrado"
    assert 'silver' in schemas, "Schema silver não encontrado"
    assert 'gold' in schemas, "Schema gold não encontrado"
