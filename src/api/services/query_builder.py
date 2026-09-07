from typing import Optional, List, Any
from sqlalchemy import select, Select
from src.api.db.models import fato_atividade_fisica, dim_tempo, dim_cidade, dim_perfil
from src.api.schemas.filters import QueryFilters

# Mapeamento declarativo de filtros: (nome_atributo, coluna_banco, tipo_operacao)
FILTER_MAPPINGS = (
    ("ano", dim_tempo.c.ano_coleta, "in"),
    ("cidade", dim_cidade.c.nome_cidade, "in"),
    ("sexo", dim_perfil.c.sexo, "eq"),
    ("faixa_etaria", dim_perfil.c.faixa_etaria, "in"),
    ("escolaridade", dim_perfil.c.faixa_escolaridade, "in"),
    ("raca_cor", dim_perfil.c.raca_cor, "in"),
)


def get_base_query() -> Select:
    """
    Constrói a base da query SQL com os JOINs do Star Schema.
    """
    return (
        select(fato_atividade_fisica)
        .join(dim_tempo, fato_atividade_fisica.c.sk_tempo == dim_tempo.c.sk_tempo)
        .join(dim_cidade, fato_atividade_fisica.c.sk_cidade == dim_cidade.c.sk_cidade)
        .join(dim_perfil, fato_atividade_fisica.c.sk_perfil == dim_perfil.c.sk_perfil)
    )


def is_valid_filter(val: Any) -> bool:
    """Verifica se o filtro possui um valor real, ignorando None, coleções vazias e objetos Query default."""
    if val is None or hasattr(val, "default"):
        return False
    if isinstance(val, (list, tuple, set)) and len(val) == 0:
        return False
    return True


def apply_filters(
    query: Select, filters: QueryFilters, exclude: Optional[List[str]] = None
) -> Select:
    """
    Aplica as condições WHERE baseadas nos filtros preenchidos pelo usuário,
    permitindo omitir campos específicos (ex: para comparativos por sexo ou idade - LOD).
    """
    exclude_set = set(exclude) if exclude else set()

    for field_name, column, op in FILTER_MAPPINGS:
        if field_name in exclude_set:
            continue
        val = getattr(filters, field_name, None)
        if not is_valid_filter(val):
            continue
        if op == "in":
            query = query.where(column.in_(val))
        elif op == "eq":
            query = query.where(column == val)

    return query
