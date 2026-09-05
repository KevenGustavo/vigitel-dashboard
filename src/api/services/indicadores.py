import time
from collections import OrderedDict
from typing import List, Optional, Any, Tuple
from sqlalchemy import select, func, case, cast, Numeric
from sqlalchemy.sql.elements import Label
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.db.models import fato_atividade_fisica, dim_tempo, dim_cidade, dim_perfil
from src.api.services.query_builder import get_base_query, apply_filters
from src.api.schemas.filters import QueryFilters
from src.api.schemas.indicators import (
    AtividadeFisicaResponse, SedentarismoResponse, DesfechosSaudeResponse,
    EvolucaoAtividadeFisica, EvolucaoSedentarismo, EvolucaoDesfechosSaude,
    ComparativoSexoResponse, SedentarismoFaixaEtariaItem, RankingCidadeItem
)

# ─── Mapeamentos e Constantes Estáticas ────────────────────────────────────────

INDICADORES_DESFECHOS_MAP = {
    'obesidade': fato_atividade_fisica.c.ind_obesidade,
    'excesso_peso': fato_atividade_fisica.c.ind_excesso_peso,
    'hipertensao': fato_atividade_fisica.c.ind_hipertensao,
    'diabetes': fato_atividade_fisica.c.ind_diabetes,
    'depressao': fato_atividade_fisica.c.ind_depressao
}

FAIXAS_ETARIAS_ORDEM = {
    '18-24': 1,
    '25-34': 2,
    '35-44': 3,
    '45-54': 4,
    '55-64': 5,
    '65+': 6
}

# ─── Expressões SQL Epidemiológicas Ponderadas ─────────────────────────────────

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

def get_atividade_fisica_columns() -> Tuple[Label, ...]:
    """Retorna as colunas SQL padronizadas dos indicadores de atividade física."""
    return (
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

def get_sedentarismo_columns() -> Tuple[Label, ...]:
    """Retorna as colunas SQL padronizadas dos indicadores de sedentarismo."""
    return (
        build_proportion_expr(fato_atividade_fisica.c.ind_tela_total_maior_3h).label('tempo_tela_maior_3h'),
        build_proportion_expr(fato_atividade_fisica.c.ind_tv_maior_3h).label('tempo_tv_maior_3h'),
        build_proportion_expr(fato_atividade_fisica.c.ind_tela_s_tv_maior_3h).label('tempo_tela_exceto_tv_maior_3h')
    )

def get_desfechos_columns() -> Tuple[Label, ...]:
    """Retorna as colunas SQL padronizadas dos agravos e desfechos crônicos de saúde."""
    return (
        build_proportion_expr(fato_atividade_fisica.c.ind_hipertensao).label('hipertensao'),
        build_proportion_expr(fato_atividade_fisica.c.ind_diabetes).label('diabetes'),
        build_proportion_expr(fato_atividade_fisica.c.ind_depressao).label('depressao'),
        build_proportion_expr(fato_atividade_fisica.c.ind_excesso_peso).label('excesso_peso'),
        build_proportion_expr(fato_atividade_fisica.c.ind_obesidade).label('obesidade')
    )

# ─── Cache de Memória com LRU e TTL ──────────────────────────────────────────

class TTLCache:
    """
    Cache em memória de alta performance com algoritmo LRU (Least Recently Used)
    e expiração automática por tempo (TTL - Time-To-Live).
    Evita vazamento de memória (Memory Leaks) e invalida dados defasados.
    """
    def __init__(self, maxsize: int = 2048, ttl_seconds: int = 600):
        self.maxsize = maxsize
        self.ttl = ttl_seconds
        self._data: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self.hits: int = 0
        self.misses: int = 0
        self.evictions: int = 0

    def __contains__(self, key: str) -> bool:
        if key not in self._data:
            return False
        timestamp, _ = self._data[key]
        if time.monotonic() - timestamp > self.ttl:
            del self._data[key]
            return False
        return True

    def __getitem__(self, key: str) -> Any:
        if key not in self._data:
            self.misses += 1
            raise KeyError(key)
        timestamp, value = self._data[key]
        if time.monotonic() - timestamp > self.ttl:
            del self._data[key]
            self.misses += 1
            raise KeyError(key)
        self._data.move_to_end(key)
        self.hits += 1
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        current_time = time.monotonic()
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = (current_time, value)
        if len(self._data) > self.maxsize:
            self._data.popitem(last=False)
            self.evictions += 1

    def purge_expired(self) -> None:
        now = time.monotonic()
        expired_keys = [k for k, (t, _) in self._data.items() if now - t > self.ttl]
        for k in expired_keys:
            del self._data[k]

    def clear(self) -> None:
        self._data.clear()

    def stats(self) -> dict:
        return {
            "size": len(self._data),
            "maxsize": self.maxsize,
            "ttl": self.ttl,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions
        }

    def __len__(self) -> int:
        self.purge_expired()
        return len(self._data)

GLOBAL_CACHE = TTLCache(maxsize=2048, ttl_seconds=600)

def normalize_param(val) -> str:
    if val is None or hasattr(val, "default"):
        return ""
    if isinstance(val, (list, set, tuple)):
        return ",".join(sorted(str(x) for x in val))
    return str(val)

def get_cache_key(func_name: str, filters: QueryFilters, extra: str = "") -> str:
    parts = [
        func_name,
        normalize_param(filters.ano),
        normalize_param(filters.cidade),
        normalize_param(filters.sexo),
        normalize_param(filters.faixa_etaria),
        normalize_param(filters.escolaridade),
        normalize_param(filters.raca_cor)
    ]
    if extra:
        parts.append(str(extra))
    return "|".join(parts)

# ─── Funções de KPI Estático ───────────────────────────────────────────────────

async def get_kpi_atividade_fisica(db: AsyncSession, filters: QueryFilters) -> AtividadeFisicaResponse:
    cache_key = get_cache_key("kpi_atividade_fisica", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    query = apply_filters(get_base_query(), filters)
    query = query.with_only_columns(*get_atividade_fisica_columns())
    
    result = await db.execute(query)
    row = result.mappings().first()
    
    res = AtividadeFisicaResponse(**row) if row else AtividadeFisicaResponse()
    GLOBAL_CACHE[cache_key] = res
    return res

async def get_kpi_sedentarismo(db: AsyncSession, filters: QueryFilters) -> SedentarismoResponse:
    cache_key = get_cache_key("kpi_sedentarismo", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    query = apply_filters(get_base_query(), filters)
    query = query.with_only_columns(*get_sedentarismo_columns())
    
    result = await db.execute(query)
    row = result.mappings().first()
    
    res = SedentarismoResponse(**row) if row else SedentarismoResponse()
    GLOBAL_CACHE[cache_key] = res
    return res

async def get_kpi_desfechos(db: AsyncSession, filters: QueryFilters) -> DesfechosSaudeResponse:
    cache_key = get_cache_key("kpi_desfechos", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    query = apply_filters(get_base_query(), filters)
    query = query.with_only_columns(*get_desfechos_columns())
    
    result = await db.execute(query)
    row = result.mappings().first()
    
    res = DesfechosSaudeResponse(**row) if row else DesfechosSaudeResponse()
    GLOBAL_CACHE[cache_key] = res
    return res

# ─── Funções de Evolução Histórica (Time-Series) ─────────────────────────────

async def get_evolucao_atividade_fisica(db: AsyncSession, filters: QueryFilters) -> List[EvolucaoAtividadeFisica]:
    cache_key = get_cache_key("evolucao_atividade_fisica", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    query = apply_filters(get_base_query(), filters)
    query = query.with_only_columns(
        dim_tempo.c.ano_coleta.label('ano'),
        *get_atividade_fisica_columns()
    ).group_by(dim_tempo.c.ano_coleta).order_by(dim_tempo.c.ano_coleta)
    
    result = await db.execute(query)
    rows = result.mappings().all()
    
    res = [EvolucaoAtividadeFisica(**row) for row in rows]
    GLOBAL_CACHE[cache_key] = res
    return res

async def get_evolucao_sedentarismo(db: AsyncSession, filters: QueryFilters) -> List[EvolucaoSedentarismo]:
    cache_key = get_cache_key("evolucao_sedentarismo", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    query = apply_filters(get_base_query(), filters)
    query = query.with_only_columns(
        dim_tempo.c.ano_coleta.label('ano'),
        *get_sedentarismo_columns()
    ).group_by(dim_tempo.c.ano_coleta).order_by(dim_tempo.c.ano_coleta)
    
    result = await db.execute(query)
    rows = result.mappings().all()
    
    res = [EvolucaoSedentarismo(**row) for row in rows]
    GLOBAL_CACHE[cache_key] = res
    return res

async def get_evolucao_desfechos(db: AsyncSession, filters: QueryFilters) -> List[EvolucaoDesfechosSaude]:
    cache_key = get_cache_key("evolucao_desfechos", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    query = apply_filters(get_base_query(), filters)
    query = query.with_only_columns(
        dim_tempo.c.ano_coleta.label('ano'),
        *get_desfechos_columns()
    ).group_by(dim_tempo.c.ano_coleta).order_by(dim_tempo.c.ano_coleta)
    
    result = await db.execute(query)
    rows = result.mappings().all()
    
    res = [EvolucaoDesfechosSaude(**row) for row in rows]
    GLOBAL_CACHE[cache_key] = res
    return res

# ─── Comparações Demográficas e Geográficas (LOD) ─────────────────────────────

async def get_comparativo_sexo(db: AsyncSession, filters: QueryFilters) -> ComparativoSexoResponse:
    cache_key = get_cache_key("comparativo_sexo", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    # Ignora filtro de sexo para manter o comparativo Masculino vs Feminino
    query = apply_filters(get_base_query(), filters, exclude=['sexo'])
    query = query.with_only_columns(
        dim_perfil.c.sexo.label('sexo'),
        *get_atividade_fisica_columns()
    ).group_by(dim_perfil.c.sexo)
    
    result = await db.execute(query)
    rows = result.mappings().all()
    
    masculino = None
    feminino = None
    for row in rows:
        row_dict = dict(row)
        sexo_val = str(row_dict.get('sexo', '')).strip().capitalize()
        if sexo_val == 'Masculino':
            masculino = AtividadeFisicaResponse(**row_dict)
        elif sexo_val == 'Feminino':
            feminino = AtividadeFisicaResponse(**row_dict)
            
    res = ComparativoSexoResponse(masculino=masculino, feminino=feminino)
    GLOBAL_CACHE[cache_key] = res
    return res

async def get_sedentarismo_faixa_etaria(db: AsyncSession, filters: QueryFilters) -> List[SedentarismoFaixaEtariaItem]:
    cache_key = get_cache_key("sedentarismo_faixa_etaria", filters)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    # Ignora filtro de faixa etária para mostrar a curva geracional completa
    query = apply_filters(get_base_query(), filters, exclude=['faixa_etaria'])
    query = query.with_only_columns(
        dim_perfil.c.faixa_etaria.label('faixa_etaria'),
        *get_sedentarismo_columns()
    ).group_by(dim_perfil.c.faixa_etaria)
    
    result = await db.execute(query)
    rows = result.mappings().all()
    
    sorted_rows = sorted(
        [r for r in rows if r['faixa_etaria'] in FAIXAS_ETARIAS_ORDEM],
        key=lambda x: FAIXAS_ETARIAS_ORDEM.get(x['faixa_etaria'], 99)
    )
    
    res = [SedentarismoFaixaEtariaItem(**dict(r)) for r in sorted_rows]
    GLOBAL_CACHE[cache_key] = res
    return res

async def get_desfechos_cidades(db: AsyncSession, filters: QueryFilters, indicador: str = 'obesidade') -> List[RankingCidadeItem]:
    cache_key = get_cache_key("desfechos_cidades", filters, extra=indicador)
    if cache_key in GLOBAL_CACHE:
        return GLOBAL_CACHE[cache_key]
        
    target_col = INDICADORES_DESFECHOS_MAP.get(indicador, fato_atividade_fisica.c.ind_obesidade)
    
    # Ignora filtro de cidade para rankear todas as capitais
    query = apply_filters(get_base_query(), filters, exclude=['cidade'])
    query = query.with_only_columns(
        dim_cidade.c.nome_cidade.label('nome_cidade'),
        build_proportion_expr(target_col).label('valor')
    ).group_by(dim_cidade.c.nome_cidade)
    
    result = await db.execute(query)
    rows = result.mappings().all()
    
    # Ordenar por valor decrescente, tratando None
    sorted_rows = sorted(
        rows,
        key=lambda r: float(r['valor']) if r['valor'] is not None else -1.0,
        reverse=True
    )
    
    res = [RankingCidadeItem(**dict(r)) for r in sorted_rows]
    GLOBAL_CACHE[cache_key] = res
    return res
