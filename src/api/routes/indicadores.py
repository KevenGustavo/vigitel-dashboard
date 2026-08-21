from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.database import get_db
from typing import List
from src.api.schemas.filters import QueryFilters
from src.api.schemas.indicators import (
    AtividadeFisicaResponse, SedentarismoResponse, DesfechosSaudeResponse,
    EvolucaoAtividadeFisica, EvolucaoSedentarismo, EvolucaoDesfechosSaude
)
from src.api.services.indicadores import (
    get_kpi_atividade_fisica,
    get_kpi_sedentarismo,
    get_kpi_desfechos,
    get_evolucao_atividade_fisica,
    get_evolucao_sedentarismo,
    get_evolucao_desfechos
)

router = APIRouter()

@router.get(
    "/atividade-fisica", 
    response_model=AtividadeFisicaResponse,
    summary="KPIs de Atividade Física",
    description="Retorna indicadores-chave (em porcentagem) relacionados à prática de atividades físicas nos diferentes domínios (lazer, deslocamento, ocupacional, doméstico)."
)
async def kpi_atividade_fisica(
    filters: QueryFilters = Depends(),
    db: AsyncSession = Depends(get_db)
):
    return await get_kpi_atividade_fisica(db, filters)

@router.get(
    "/sedentarismo", 
    response_model=SedentarismoResponse,
    summary="KPIs de Sedentarismo",
    description="Retorna indicadores-chave sobre comportamento sedentário (tempo de tela e TV)."
)
async def kpi_sedentarismo(
    filters: QueryFilters = Depends(),
    db: AsyncSession = Depends(get_db)
):
    return await get_kpi_sedentarismo(db, filters)

@router.get(
    "/desfechos", 
    response_model=DesfechosSaudeResponse,
    summary="KPIs de Desfechos de Saúde",
    description="Retorna os percentuais de morbidades associadas relatadas (hipertensão, diabetes, depressão)."
)
async def kpi_desfechos(
    filters: QueryFilters = Depends(),
    db: AsyncSession = Depends(get_db)
):
    return await get_kpi_desfechos(db, filters)

# ─── Endpoints de Evolução Histórica (Série Temporal) ──────────────────────────

@router.get(
    "/evolucao/atividade-fisica", 
    response_model=List[EvolucaoAtividadeFisica],
    summary="Série Histórica: Atividade Física",
    description="Retorna a evolução histórica dos KPIs de Atividade Física agrupados por ano."
)
async def evolucao_atividade_fisica(
    filters: QueryFilters = Depends(),
    db: AsyncSession = Depends(get_db)
):
    return await get_evolucao_atividade_fisica(db, filters)

@router.get(
    "/evolucao/sedentarismo", 
    response_model=List[EvolucaoSedentarismo],
    summary="Série Histórica: Sedentarismo",
    description="Retorna a evolução histórica dos KPIs de Sedentarismo agrupados por ano."
)
async def evolucao_sedentarismo(
    filters: QueryFilters = Depends(),
    db: AsyncSession = Depends(get_db)
):
    return await get_evolucao_sedentarismo(db, filters)

@router.get(
    "/evolucao/desfechos", 
    response_model=List[EvolucaoDesfechosSaude],
    summary="Série Histórica: Desfechos de Saúde",
    description="Retorna a evolução histórica dos Desfechos de Saúde (Hipertensão, Diabetes, Depressão, IMC) agrupados por ano."
)
async def evolucao_desfechos(
    filters: QueryFilters = Depends(),
    db: AsyncSession = Depends(get_db)
):
    return await get_evolucao_desfechos(db, filters)
