import pytest
from src.api.services.query_builder import get_base_query, apply_filters
from src.api.schemas.filters import QueryFilters

def test_get_base_query_structure():
    """Garante que a base query é construída com os JOINs do Star Schema."""
    query = get_base_query()
    sql_str = str(query)
    
    assert "dim_tempo" in sql_str
    assert "dim_cidade" in sql_str
    assert "dim_perfil" in sql_str
    assert "fato_atividade_fisica" in sql_str

def test_apply_filters_where_clauses():
    """Verifica se as cláusulas WHERE são adicionadas de acordo com os filtros passados."""
    filters = QueryFilters(
        ano=[2023],
        cidade=["Curitiba"],
        sexo="Feminino",
        faixa_etaria=["18-24"]
    )
    query = get_base_query()
    filtered_query = apply_filters(query, filters)
    sql_str = str(filtered_query)
    
    assert "dim_tempo.ano_coleta IN" in sql_str
    assert "dim_cidade.nome_cidade IN" in sql_str
    assert "dim_perfil.sexo =" in sql_str
    assert "dim_perfil.faixa_etaria IN" in sql_str

def test_apply_filters_with_exclude_lod():
    """Testa a exclusão de filtros específicos (LOD) para comparativos de gênero, idade e capitais."""
    filters = QueryFilters(
        ano=[2023],
        cidade=["São Paulo"],
        sexo="Masculino",
        faixa_etaria=["25-34"]
    )
    
    # 1. Simula Radar de Sexo: ignora sexo, mas mantém cidade e ano
    query_radar = apply_filters(get_base_query(), filters, exclude=["sexo"])
    sql_radar = str(query_radar)
    assert "dim_perfil.sexo =" not in sql_radar
    assert "dim_tempo.ano_coleta IN" in sql_radar
    assert "dim_cidade.nome_cidade IN" in sql_radar

    # 2. Simula Barras de Faixa Etária: ignora faixa_etaria
    query_idade = apply_filters(get_base_query(), filters, exclude=["faixa_etaria"])
    sql_idade = str(query_idade)
    assert "dim_perfil.faixa_etaria IN" not in sql_idade
    assert "dim_perfil.sexo =" in sql_idade

    # 3. Simula Ranking de Capitais: ignora cidade para rankear todas as 27
    query_ranking = apply_filters(get_base_query(), filters, exclude=["cidade"])
    sql_ranking = str(query_ranking)
    assert "dim_cidade.nome_cidade IN" not in sql_ranking
    assert "dim_perfil.sexo =" in sql_ranking
