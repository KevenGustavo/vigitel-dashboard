from typing import List
from sqlalchemy import select, func, case, cast, Numeric
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.db.models import fato_atividade_fisica, dim_tempo
from src.api.services.query_builder import get_base_query, apply_filters
from src.api.schemas.filters import QueryFilters
from src.api.schemas.indicators import (
    AtividadeFisicaResponse, SedentarismoResponse, DesfechosSaudeResponse,
    EvolucaoAtividadeFisica, EvolucaoSedentarismo, EvolucaoDesfechosSaude
)

def build_proportion_expr(*columns):
    """
    Constrói a expressão SQL para calcular a prevalência epidemiológica com pesos.
    Fórmula: SUM(peso_amostral) FILTER (WHERE coalesce(cols...) IS TRUE) / SUM(peso) FILTER (WHERE coalesce(cols...) IS NOT NULL)
    Como as variáveis do VIGITEL mudam de nome ao longo dos anos, passamos múltiplas colunas como fallback (COALESCE).
    """
    coalesced_col = func.coalesce(*columns)
    
    num = func.sum(case((coalesced_col.is_(True), fato_atividade_fisica.c.peso_amostral), else_=0))
    den = func.sum(case((coalesced_col.isnot(None), fato_atividade_fisica.c.peso_amostral), else_=0))
    
    return case(
        (den > 0, cast((num / den) * 100, Numeric(10, 2))),
        else_=None
    )

# ─── Cache de Memória ─────────────────────────────────

GLOBAL_CACHE = {}

def get_cache_key(func_name: str, filters: QueryFilters) -> str:
    parts = [
        func_name,
        str(filters.ano),
        str(filters.cidade),
        str(filters.sexo),
        str(filters.faixa_etaria),
        str(filters.escolaridade),
        str(filters.raca_cor)
    ]
    return "|".join(parts)

# ─── Funções de KPI Estático ───────────────────────────────────────────────────

async def get_kpi_atividade_fisica(db: AsyncSession, filters: QueryFilters) -> AtividadeFisicaResponse:
    cache_key = get_cache_key("kpi_atividade_fisica", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    query = get_base_query()
    query = apply_filters(query, filters)
    
    query = query.with_only_columns(
        build_proportion_expr(
            fato_atividade_fisica.c.ind_ativo_lazer, 
            fato_atividade_fisica.c.ind_ativo_lazer_150min
        ).label('ativo_lazer'),
        build_proportion_expr(fato_atividade_fisica.c.ind_ativo_transporte).label('ativo_deslocamento'),
        build_proportion_expr(fato_atividade_fisica.c.ind_ativo_ocupacional).label('ativo_ocupacional'),
        build_proportion_expr(fato_atividade_fisica.c.ind_ativo_domestico).label('ativo_domestico'),
        build_proportion_expr(
            fato_atividade_fisica.c.ind_inativo_total, 
            fato_atividade_fisica.c.ind_inativo_lazer
        ).label('inativo_total'),
        build_proportion_expr(
            fato_atividade_fisica.c.ind_af_3dominios_150min, 
            fato_atividade_fisica.c.ind_af_4dominios_150min
        ).label('atinge_150min')
    )
    
    result = await db.execute(query)
    row = result.mappings().first()
    
    GLOBAL_CACHE[cache_key] = AtividadeFisicaResponse(**row)
    return GLOBAL_CACHE[cache_key]

async def get_kpi_sedentarismo(db: AsyncSession, filters: QueryFilters) -> SedentarismoResponse:
    cache_key = get_cache_key("kpi_sedentarismo", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    query = get_base_query()
    query = apply_filters(query, filters)
    
    query = query.with_only_columns(
        build_proportion_expr(fato_atividade_fisica.c.ind_tela_total_maior_3h).label('tempo_tela_maior_3h'),
        build_proportion_expr(fato_atividade_fisica.c.ind_tv_maior_3h).label('tempo_tv_maior_3h'),
        build_proportion_expr(fato_atividade_fisica.c.ind_tela_s_tv_maior_3h).label('tempo_tela_exceto_tv_maior_3h')
    )
    
    result = await db.execute(query)
    row = result.mappings().first()
    
    GLOBAL_CACHE[cache_key] = SedentarismoResponse(**row)
    return GLOBAL_CACHE[cache_key]

async def get_kpi_desfechos(db: AsyncSession, filters: QueryFilters) -> DesfechosSaudeResponse:
    cache_key = get_cache_key("kpi_desfechos", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    query = get_base_query()
    query = apply_filters(query, filters)
    
    query = query.with_only_columns(
        build_proportion_expr(fato_atividade_fisica.c.ind_hipertensao).label('hipertensao'),
        build_proportion_expr(fato_atividade_fisica.c.ind_diabetes).label('diabetes'),
        build_proportion_expr(fato_atividade_fisica.c.ind_depressao).label('depressao'),
        build_proportion_expr(fato_atividade_fisica.c.ind_excesso_peso).label('excesso_peso'),
        build_proportion_expr(fato_atividade_fisica.c.ind_obesidade).label('obesidade')
    )
    
    result = await db.execute(query)
    row = result.mappings().first()
    
    GLOBAL_CACHE[cache_key] = DesfechosSaudeResponse(**row)
    return GLOBAL_CACHE[cache_key]

# ─── Funções de Evolução Histórica (Time-Series) ─────────────────────────────

async def get_evolucao_atividade_fisica(db: AsyncSession, filters: QueryFilters) -> List[EvolucaoAtividadeFisica]:
    cache_key = get_cache_key("evolucao_atividade_fisica", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    query = get_base_query()
    query = apply_filters(query, filters)
    
    query = query.with_only_columns(
        dim_tempo.c.ano_coleta.label('ano'),
        build_proportion_expr(
            fato_atividade_fisica.c.ind_ativo_lazer, 
            fato_atividade_fisica.c.ind_ativo_lazer_150min
        ).label('ativo_lazer'),
        build_proportion_expr(fato_atividade_fisica.c.ind_ativo_transporte).label('ativo_deslocamento'),
        build_proportion_expr(fato_atividade_fisica.c.ind_ativo_ocupacional).label('ativo_ocupacional'),
        build_proportion_expr(fato_atividade_fisica.c.ind_ativo_domestico).label('ativo_domestico'),
        build_proportion_expr(
            fato_atividade_fisica.c.ind_inativo_total, 
            fato_atividade_fisica.c.ind_inativo_lazer
        ).label('inativo_total'),
        build_proportion_expr(
            fato_atividade_fisica.c.ind_af_3dominios_150min, 
            fato_atividade_fisica.c.ind_af_4dominios_150min
        ).label('atinge_150min')
    )
    
    # Agrupamento e Ordenação por Ano
    query = query.group_by(dim_tempo.c.ano_coleta).order_by(dim_tempo.c.ano_coleta)
    
    result = await db.execute(query)
    rows = result.mappings().all()
    
    GLOBAL_CACHE[cache_key] = [EvolucaoAtividadeFisica(**row) for row in rows]
    return GLOBAL_CACHE[cache_key]

async def get_evolucao_sedentarismo(db: AsyncSession, filters: QueryFilters) -> List[EvolucaoSedentarismo]:
    cache_key = get_cache_key("evolucao_sedentarismo", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    query = get_base_query()
    query = apply_filters(query, filters)
    
    query = query.with_only_columns(
        dim_tempo.c.ano_coleta.label('ano'),
        build_proportion_expr(fato_atividade_fisica.c.ind_tela_total_maior_3h).label('tempo_tela_maior_3h'),
        build_proportion_expr(fato_atividade_fisica.c.ind_tv_maior_3h).label('tempo_tv_maior_3h'),
        build_proportion_expr(fato_atividade_fisica.c.ind_tela_s_tv_maior_3h).label('tempo_tela_exceto_tv_maior_3h')
    )
    
    query = query.group_by(dim_tempo.c.ano_coleta).order_by(dim_tempo.c.ano_coleta)
    
    result = await db.execute(query)
    rows = result.mappings().all()
    
    GLOBAL_CACHE[cache_key] = [EvolucaoSedentarismo(**row) for row in rows]
    return GLOBAL_CACHE[cache_key]

async def get_evolucao_desfechos(db: AsyncSession, filters: QueryFilters) -> List[EvolucaoDesfechosSaude]:
    cache_key = get_cache_key("evolucao_desfechos", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    query = get_base_query()
    query = apply_filters(query, filters)
    
    query = query.with_only_columns(
        dim_tempo.c.ano_coleta.label('ano'),
        build_proportion_expr(fato_atividade_fisica.c.ind_hipertensao).label('hipertensao'),
        build_proportion_expr(fato_atividade_fisica.c.ind_diabetes).label('diabetes'),
        build_proportion_expr(fato_atividade_fisica.c.ind_depressao).label('depressao'),
        build_proportion_expr(fato_atividade_fisica.c.ind_excesso_peso).label('excesso_peso'),
        build_proportion_expr(fato_atividade_fisica.c.ind_obesidade).label('obesidade')
    )
    
    query = query.group_by(dim_tempo.c.ano_coleta).order_by(dim_tempo.c.ano_coleta)
    
    result = await db.execute(query)
    rows = result.mappings().all()
    
    GLOBAL_CACHE[cache_key] = [EvolucaoDesfechosSaude(**row) for row in rows]
    return GLOBAL_CACHE[cache_key]
