import pytest
from httpx import AsyncClient

# Permite que os testes assíncronos rodem
pytestmark = pytest.mark.asyncio(scope="session")

async def test_health_check(async_client: AsyncClient):
    """Verifica se a API está online."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

async def test_get_filtros(async_client: AsyncClient):
    """Verifica se o endpoint de filtros retorna os dados estruturados corretos."""
    response = await async_client.get("/api/v1/filtros")
    assert response.status_code == 200
    data = response.json()
    
    # Validações de chaves essenciais ditadas pelo Pydantic Schema
    assert "anos" in data
    assert "cidades" in data
    assert "racas_cores" in data
    
    # Validação de conteúdo: deve haver múltiplos anos, incluindo 2024
    assert isinstance(data["anos"], list)
    assert len(data["anos"]) > 0
    assert 2024 in data["anos"]
    
    # Validação de que não existem valores nulos (None) mascarados nos filtros textuais
    assert None not in data["racas_cores"]

async def test_kpi_atividade_fisica(async_client: AsyncClient):
    """Verifica o endpoint de Atividade Física com um filtro simples."""
    response = await async_client.get("/api/v1/indicadores/atividade-fisica?ano=2024")
    assert response.status_code == 200
    data = response.json()
    
    assert "ativo_lazer" in data
    assert "ativo_deslocamento" in data
    
    # Valores devem ser proporções float
    assert isinstance(data["ativo_lazer"], float)

async def test_kpi_sedentarismo_multiple_filters(async_client: AsyncClient):
    """Verifica o endpoint de Sedentarismo aplicando múltiplos filtros concatenados."""
    response = await async_client.get("/api/v1/indicadores/sedentarismo?ano=2024&sexo=masculino&cidade=goiania")
    assert response.status_code == 200
    data = response.json()
    
    assert "tempo_tela_maior_3h" in data
    assert "tempo_tv_maior_3h" in data
    
    assert isinstance(data["tempo_tela_maior_3h"], float)

async def test_kpi_desfechos(async_client: AsyncClient):
    """Verifica o endpoint de Desfechos e seu Pydantic Schema de retorno."""
    response = await async_client.get("/api/v1/indicadores/desfechos?ano=2024")
    assert response.status_code == 200
    data = response.json()
    
    assert "hipertensao" in data
    assert "diabetes" in data
    assert "depressao" in data
    assert "excesso_peso" in data
    assert "obesidade" in data
    
    assert isinstance(data["excesso_peso"], float)
    assert isinstance(data["obesidade"], float)
    assert data["hipertensao"] is None or isinstance(data["hipertensao"], float)
    assert data["diabetes"] is None or isinstance(data["diabetes"], float)
    assert data["depressao"] is None or isinstance(data["depressao"], float)

async def test_evolucao_atividade_fisica(async_client: AsyncClient):
    """Verifica se o endpoint de evolução retorna um array de série histórica."""
    response = await async_client.get("/api/v1/indicadores/evolucao/atividade-fisica?cidade=sao paulo")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    assert "ano" in data[0]
    assert "ativo_lazer" in data[0]

async def test_evolucao_desfechos(async_client: AsyncClient):
    """Verifica o endpoint de evolução de desfechos (Time-Series)."""
    response = await async_client.get("/api/v1/indicadores/evolucao/desfechos")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    assert "ano" in data[0]
    assert "excesso_peso" in data[0]

async def test_invalid_param_type(async_client: AsyncClient):
    """Garante que a API e o Pydantic bloqueiam tipos de dados inválidos."""
    # Passando uma string onde um ano (int) é exigido
    response = await async_client.get("/api/v1/indicadores/atividade-fisica?ano=abc")
    assert response.status_code == 422 # Unprocessable Entity (Falha de validação do FastAPI)
