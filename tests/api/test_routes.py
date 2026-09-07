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

    # Validação de ordenação lógica de escolaridade (0-8 anos -> 9-11 anos -> 12+ anos -> Não informado)
    escolaridades = data["escolaridades"]
    assert isinstance(escolaridades, list)
    if "0-8 anos" in escolaridades and "9-11 anos" in escolaridades and "12+ anos" in escolaridades:
        idx_0_8 = escolaridades.index("0-8 anos")
        idx_9_11 = escolaridades.index("9-11 anos")
        idx_12_plus = escolaridades.index("12+ anos")
        assert idx_0_8 < idx_9_11 < idx_12_plus, f"Ordem de escolaridade incorreta: {escolaridades}"
    if "Não informado" in escolaridades:
        assert escolaridades[-1] == "Não informado", "'Não informado' deve ser a última opção de escolaridade"

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

async def test_dashboard_consolidado_success(async_client: AsyncClient):
    """Verifica que o endpoint consolidado (BFF) retorna todos os 9 blocos com integridade e tipo correto."""
    response = await async_client.get("/api/v1/indicadores/dashboard?ano=2023")
    assert response.status_code == 200
    data = response.json()

    # Verifica os 3 blocos de KPIs
    assert "atividade_fisica" in data
    assert "sedentarismo" in data
    assert "desfechos" in data
    assert data["atividade_fisica"]["atinge_150min"] is not None
    assert data["sedentarismo"]["tempo_tela_maior_3h"] is not None
    assert data["desfechos"]["obesidade"] is not None

    # Verifica as 3 séries temporais
    assert "evolucao_atividade_fisica" in data
    assert "evolucao_sedentarismo" in data
    assert "evolucao_desfechos" in data
    assert isinstance(data["evolucao_atividade_fisica"], list)
    assert isinstance(data["evolucao_sedentarismo"], list)
    assert isinstance(data["evolucao_desfechos"], list)

    # Verifica as 3 análises comparativas e de distribuição
    assert "comparativo_sexo" in data
    assert data["comparativo_sexo"]["masculino"] is not None
    assert data["comparativo_sexo"]["feminino"] is not None

    assert "sedentarismo_faixa_etaria" in data
    assert isinstance(data["sedentarismo_faixa_etaria"], list)
    assert len(data["sedentarismo_faixa_etaria"]) > 0

    assert "ranking_cidades" in data
    assert isinstance(data["ranking_cidades"], list)
    assert len(data["ranking_cidades"]) == 27

async def test_dashboard_consolidado_with_filters(async_client: AsyncClient):
    """Verifica o endpoint consolidado com filtros demográficos e indicador de ranking customizado."""
    response = await async_client.get(
        "/api/v1/indicadores/dashboard?ano=2023&cidade=São Paulo&indicador_ranking=diabetes"
    )
    assert response.status_code == 200
    data = response.json()

    assert data["atividade_fisica"] is not None
    assert data["desfechos"]["obesidade"] is not None
    assert len(data["ranking_cidades"]) == 27

    # Garante que ranking está ordenado decrescente
    valores = [item["valor"] for item in data["ranking_cidades"] if item["valor"] is not None]
    assert valores == sorted(valores, reverse=True)

async def test_cache_control_headers(async_client: AsyncClient):
    """Verifica que respostas analíticas incluem cabeçalhos de cache para CDN e o health check impede cache."""
    # Rota analítica consolidada
    res_dash = await async_client.get("/api/v1/indicadores/dashboard?ano=2023")
    assert res_dash.status_code == 200
    assert "cache-control" in res_dash.headers
    cc_dash = res_dash.headers["cache-control"]
    assert "public" in cc_dash
    assert "max-age=3600" in cc_dash
    assert "s-maxage=86400" in cc_dash

    # Rota de filtros
    res_filtros = await async_client.get("/api/v1/filtros")
    assert res_filtros.status_code == 200
    assert "cache-control" in res_filtros.headers
    assert "public" in res_filtros.headers["cache-control"]

    # Rota de health check não deve ser pública para cache
    res_health = await async_client.get("/health")
    assert res_health.status_code == 200
    assert "no-store" in res_health.headers.get("cache-control", "")


