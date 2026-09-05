import time
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.db.models import dim_tempo, dim_cidade, dim_perfil
from src.api.schemas.filters import FiltrosDisponiveis

# Cache em memória para os filtros disponíveis (dimensões são estáticas durante o runtime da API)
_CACHED_FILTERS: Optional[FiltrosDisponiveis] = None
_CACHED_AT: float = 0.0
_CACHE_TTL: float = 3600.0  # 1 hora

def clear_filtros_cache() -> None:
    """Invalida o cache de filtros (útil para testes ou após re-execução de ETL)."""
    global _CACHED_FILTERS, _CACHED_AT
    _CACHED_FILTERS = None
    _CACHED_AT = 0.0

async def get_filtros_disponiveis(db: AsyncSession) -> FiltrosDisponiveis:
    """
    Busca todas as opções únicas do Star Schema para popular os filtros da interface gráfica.
    Utiliza cache em memória com TTL de 1h para evitar consultas repetitivas ao banco a cada requisição.
    """
    global _CACHED_FILTERS, _CACHED_AT

    now = time.time()
    if _CACHED_FILTERS is not None and (now - _CACHED_AT) < _CACHE_TTL:
        return _CACHED_FILTERS

    # Anos
    anos_query = select(dim_tempo.c.ano_coleta).distinct().order_by(dim_tempo.c.ano_coleta.desc())
    anos = (await db.execute(anos_query)).scalars().all()
    
    # Cidades
    cidades_query = select(dim_cidade.c.nome_cidade).distinct().order_by(dim_cidade.c.nome_cidade)
    cidades_result = await db.execute(cidades_query)
    cidades = [{"nome_cidade": row.nome_cidade} for row in cidades_result.mappings()]
    
    # Sexo
    sexos_query = select(dim_perfil.c.sexo).where(dim_perfil.c.sexo.is_not(None)).distinct().order_by(dim_perfil.c.sexo)
    sexos = (await db.execute(sexos_query)).scalars().all()
    
    # Faixa Etária
    faixas_query = select(dim_perfil.c.faixa_etaria).where(dim_perfil.c.faixa_etaria.is_not(None)).distinct().order_by(dim_perfil.c.faixa_etaria)
    faixas = (await db.execute(faixas_query)).scalars().all()
    
    # Escolaridade
    escolaridade_query = select(dim_perfil.c.faixa_escolaridade).where(dim_perfil.c.faixa_escolaridade.is_not(None)).distinct().order_by(dim_perfil.c.faixa_escolaridade)
    escolaridades = (await db.execute(escolaridade_query)).scalars().all()
    
    # Raça/Cor
    racas_query = select(dim_perfil.c.raca_cor).where(dim_perfil.c.raca_cor.is_not(None)).distinct().order_by(dim_perfil.c.raca_cor)
    racas = (await db.execute(racas_query)).scalars().all()
    
    filtros = FiltrosDisponiveis(
        anos=list(anos),
        cidades=cidades,
        faixas_etarias=list(faixas),
        escolaridades=list(escolaridades),
        sexos=list(sexos),
        racas_cores=list(racas)
    )

    _CACHED_FILTERS = filtros
    _CACHED_AT = now
    return filtros
