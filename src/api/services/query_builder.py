from sqlalchemy import select
from src.api.db.models import fato_atividade_fisica, dim_tempo, dim_cidade, dim_perfil
from src.api.schemas.filters import QueryFilters

def get_base_query():
    """
    Constrói a base da query SQL com os JOINs do Star Schema.
    """
    return select(fato_atividade_fisica).join(
        dim_tempo, fato_atividade_fisica.c.sk_tempo == dim_tempo.c.sk_tempo
    ).join(
        dim_cidade, fato_atividade_fisica.c.sk_cidade == dim_cidade.c.sk_cidade
    ).join(
        dim_perfil, fato_atividade_fisica.c.sk_perfil == dim_perfil.c.sk_perfil
    )

def apply_filters(query, filters: QueryFilters):
    """
    Aplica as condições WHERE baseadas nos filtros preenchidos pelo usuário.
    """
    if filters.ano:
        query = query.where(dim_tempo.c.ano_coleta.in_(filters.ano))
    if filters.cidade:
        query = query.where(dim_cidade.c.id_cidade.in_(filters.cidade))
    if filters.sexo:
        query = query.where(dim_perfil.c.sexo == filters.sexo)
    if filters.faixa_etaria:
        query = query.where(dim_perfil.c.faixa_etaria.in_(filters.faixa_etaria))
    if filters.escolaridade:
        query = query.where(dim_perfil.c.faixa_escolaridade.in_(filters.escolaridade))
    if filters.raca_cor:
        query = query.where(dim_perfil.c.raca_cor.in_(filters.raca_cor))
    
    return query
