import pytest
from httpx import AsyncClient

# Permite que os testes assíncronos rodem na sessão
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
    assert "sexos" in data
    assert "faixas_etarias" in data
    assert "escolaridades" in data
    
    # Validação de conteúdo: deve haver múltiplos anos, incluindo 2024
    assert isinstance(data["anos"], list)
    assert len(data["anos"]) > 0
    assert 2024 in data["anos"]
    
    # Validação de que não existem valores nulos mascarados nos filtros
    assert None not in data["racas_cores"]
    assert len(data["cidades"]) == 27

async def test_kpi_atividade_fisica(async_client: AsyncClient):
    """Verifica o endpoint de Atividade Física com um filtro simples de ano."""
    response = await async_client.get("/api/v1/indicadores/atividade-fisica?ano=2024")
    assert response.status_code == 200
    data = response.json()
    
    assert "ativo_lazer" in data
    assert "ativo_deslocamento" in data
    assert "atinge_150min" in data
    
    # Valores devem ser proporções float ou None se não houver coleta
    assert isinstance(data["ativo_lazer"], float)

async def test_kpi_sedentarismo_multiple_filters(async_client: AsyncClient):
    """Verifica o endpoint de Sedentarismo aplicando múltiplos filtros concatenados."""
    response = await async_client.get("/api/v1/indicadores/sedentarismo?ano=2024&sexo=Masculino&cidade=Goiânia")
    assert response.status_code == 200
    data = response.json()
    
    assert "tempo_tela_maior_3h" in data
    assert "tempo_tv_maior_3h" in data
    assert "tempo_tela_exceto_tv_maior_3h" in data
    
    assert isinstance(data["tempo_tela_maior_3h"], float)

async def test_kpi_desfechos(async_client: AsyncClient):
    """Verifica o endpoint de Desfechos de Saúde e seu Pydantic Schema de retorno."""
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

async def test_evolucao_atividade_fisica(async_client: AsyncClient):
    """Verifica se o endpoint de evolução retorna um array de série histórica."""
    response = await async_client.get("/api/v1/indicadores/evolucao/atividade-fisica?cidade=São Paulo")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    assert "ano" in data[0]
    assert "ativo_lazer" in data[0]

async def test_evolucao_sedentarismo(async_client: AsyncClient):
    """Verifica o endpoint de evolução histórica de sedentarismo (TV vs Telas Digitais)."""
    response = await async_client.get("/api/v1/indicadores/evolucao/sedentarismo")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    assert "ano" in data[0]
    assert "tempo_tv_maior_3h" in data[0]
    assert "tempo_tela_maior_3h" in data[0]

async def test_evolucao_desfechos(async_client: AsyncClient):
    """Verifica o endpoint de evolução de desfechos crônicos (Time-Series)."""
    response = await async_client.get("/api/v1/indicadores/evolucao/desfechos")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    assert "ano" in data[0]
    assert "excesso_peso" in data[0]
    assert "obesidade" in data[0]

async def test_comparativo_sexo(async_client: AsyncClient):
    """Verifica o endpoint de comparação intergênero de atividade física (Radar Chart)."""
    response = await async_client.get("/api/v1/indicadores/comparativo/sexo?ano=2023")
    assert response.status_code == 200
    data = response.json()
    
    assert "masculino" in data
    assert "feminino" in data
    assert data["masculino"] is not None
    assert data["feminino"] is not None
    assert "ativo_lazer" in data["masculino"]
    assert "ativo_domestico" in data["feminino"]

async def test_sedentarismo_faixa_etaria(async_client: AsyncClient):
    """Verifica o endpoint de distribuição de sedentarismo por grupos etários (Bar Chart)."""
    response = await async_client.get("/api/v1/indicadores/sedentarismo/faixa-etaria?ano=2023")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    faixas = [item["faixa_etaria"] for item in data]
    assert "18-24" in faixas
    assert "65+" in faixas

async def test_desfechos_cidades_ranking(async_client: AsyncClient):
    """Verifica o ranking geográfico das 27 capitais por indicador de agravo crônico."""
    for indicador in ["obesidade", "excesso_peso", "diabetes", "hipertensao"]:
        response = await async_client.get(f"/api/v1/indicadores/desfechos/cidades?indicador={indicador}&ano=2023")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 27
        assert "nome_cidade" in data[0]
        assert "valor" in data[0]
        
        # Garante ordenação estritamente decrescente
        valores = [item["valor"] for item in data if item["valor"] is not None]
        assert valores == sorted(valores, reverse=True)

async def test_invalid_param_type(async_client: AsyncClient):
    """Garante que a API e o Pydantic bloqueiam tipos de dados inválidos com HTTP 422."""
    response = await async_client.get("/api/v1/indicadores/atividade-fisica?ano=abc")
    assert response.status_code == 422
