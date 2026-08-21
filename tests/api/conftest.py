import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.api.main import app

@pytest_asyncio.fixture(scope="session")
async def async_client():
    """Cria um cliente assíncrono do httpx atrelado à aplicação FastAPI para simular requisições HTTP reais sem precisar subir a porta."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
