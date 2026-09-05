import pytest
import time
from src.api.services.indicadores import TTLCache, normalize_param, get_cache_key
from src.api.schemas.filters import QueryFilters

def test_ttl_cache_basic_operations():
    """Testa inserção, leitura e pertencimento no TTLCache."""
    cache = TTLCache(maxsize=10, ttl_seconds=60)
    cache["chave_1"] = {"status": "ok"}
    
    assert "chave_1" in cache
    assert "chave_inexistente" not in cache
    assert cache["chave_1"] == {"status": "ok"}
    assert len(cache) == 1

def test_ttl_cache_lru_eviction():
    """Testa se a política LRU descarta o item mais antigo ao ultrapassar maxsize."""
    cache = TTLCache(maxsize=3, ttl_seconds=60)
    cache["item_1"] = 1
    cache["item_2"] = 2
    cache["item_3"] = 3
    
    assert len(cache) == 3
    # Acessa item_1 para movê-lo ao final (mais recentemente usado)
    _ = cache["item_1"]
    
    # Adiciona item_4: deve expulsar item_2 (o menos recentemente usado)
    cache["item_4"] = 4
    
    assert len(cache) == 3
    assert "item_1" in cache
    assert "item_3" in cache
    assert "item_4" in cache
    assert "item_2" not in cache

def test_ttl_cache_expiration():
    """Testa se itens com tempo superior a ttl_seconds são invalidados automaticamente."""
    cache = TTLCache(maxsize=10, ttl_seconds=1)
    cache["temporario"] = "valor"
    
    assert "temporario" in cache
    time.sleep(1.1)
    
    # Após 1.1s, deve ter expirado
    assert "temporario" not in cache
    assert len(cache) == 0

def test_ttl_cache_clear():
    """Testa a limpeza manual de todo o cache."""
    cache = TTLCache(maxsize=10, ttl_seconds=60)
    cache["a"] = 1
    cache["b"] = 2
    cache.clear()
    assert len(cache) == 0
    assert "a" not in cache

def test_normalize_param_ordering():
    """Testa se a normalização de listas e parâmetros garante a mesma chave independente da ordem."""
    lista_1 = ["São Paulo", "Rio de Janeiro", "Belo Horizonte"]
    lista_2 = ["Rio de Janeiro", "São Paulo", "Belo Horizonte"]
    
    assert normalize_param(lista_1) == normalize_param(lista_2)
    assert normalize_param(None) == ""
    assert normalize_param("Simples") == "Simples"

def test_get_cache_key_canonical():
    """Testa se dois objetos QueryFilters equivalentes geram rigorosamente a mesma chave."""
    f1 = QueryFilters(cidade=["São Paulo", "Curitiba"], ano=[2023, 2024])
    f2 = QueryFilters(cidade=["Curitiba", "São Paulo"], ano=[2024, 2023])
    
    k1 = get_cache_key("kpi_atividade", f1)
    k2 = get_cache_key("kpi_atividade", f2)
    
    assert k1 == k2
    assert "Curitiba,São Paulo" in k1
    assert "2023,2024" in k1

def test_get_cache_key_with_extra():
    """Testa se o parâmetro extra (usado no ranking de cidades) é incorporado na chave."""
    f = QueryFilters(ano=[2024])
    k_obesidade = get_cache_key("desfechos_cidades", f, extra="obesidade")
    k_diabetes = get_cache_key("desfechos_cidades", f, extra="diabetes")
    
    assert k_obesidade != k_diabetes
    assert k_obesidade.endswith("|obesidade")
    assert k_diabetes.endswith("|diabetes")
