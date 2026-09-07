from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Literal

from src.api.db.database import get_db
from src.api.schemas.filters import QueryFilters
from src.api.schemas.indicators import (
    AtividadeFisicaResponse,
    SedentarismoResponse,
    DesfechosSaudeResponse,
    EvolucaoAtividadeFisica,
    EvolucaoSedentarismo,
    EvolucaoDesfechosSaude,
    ComparativoSexoResponse,
    SedentarismoFaixaEtariaItem,
    RankingCidadeItem,
    DashboardConsolidadoResponse,
)
from src.api.services.indicadores import (
    get_kpi_atividade_fisica,
    get_kpi_sedentarismo,
    get_kpi_desfechos,
    get_evolucao_atividade_fisica,
    get_evolucao_sedentarismo,
    get_evolucao_desfechos,
    get_comparativo_sexo,
    get_sedentarismo_faixa_etaria,
    get_desfechos_cidades,
    get_dashboard_consolidado,
)

router = APIRouter()


@router.get(
    "/atividade-fisica",
    response_model=AtividadeFisicaResponse,
    status_code=status.HTTP_200_OK,
    summary="KPIs de Atividade Física",
    description="Retorna indicadores-chave (em porcentagem) relacionados à prática de atividades físicas nos diferentes domínios (lazer, deslocamento, ocupacional, doméstico).",
)
async def kpi_atividade_fisica(
    filters: QueryFilters = Depends(), db: AsyncSession = Depends(get_db)
):
    return await get_kpi_atividade_fisica(db, filters)


@router.get(
    "/sedentarismo",
    response_model=SedentarismoResponse,
    status_code=status.HTTP_200_OK,
    summary="KPIs de Sedentarismo",
    description="Retorna indicadores-chave sobre comportamento sedentário (tempo de tela e TV).",
)
async def kpi_sedentarismo(filters: QueryFilters = Depends(), db: AsyncSession = Depends(get_db)):
    return await get_kpi_sedentarismo(db, filters)


@router.get(
    "/desfechos",
    response_model=DesfechosSaudeResponse,
    status_code=status.HTTP_200_OK,
    summary="KPIs de Desfechos de Saúde",
    description="Retorna os percentuais de morbidades associadas relatadas (hipertensão, diabetes, depressão).",
)
async def kpi_desfechos(filters: QueryFilters = Depends(), db: AsyncSession = Depends(get_db)):
    return await get_kpi_desfechos(db, filters)


# ─── Endpoints de Evolução Histórica (Série Temporal) ──────────────────────────


@router.get(
    "/evolucao/atividade-fisica",
    response_model=List[EvolucaoAtividadeFisica],
    status_code=status.HTTP_200_OK,
    summary="Série Histórica: Atividade Física",
    description="Retorna a evolução histórica dos KPIs de Atividade Física agrupados por ano.",
)
async def evolucao_atividade_fisica(
    filters: QueryFilters = Depends(), db: AsyncSession = Depends(get_db)
):
    return await get_evolucao_atividade_fisica(db, filters)


@router.get(
    "/evolucao/sedentarismo",
    response_model=List[EvolucaoSedentarismo],
    status_code=status.HTTP_200_OK,
    summary="Série Histórica: Sedentarismo",
    description="Retorna a evolução histórica dos KPIs de Sedentarismo agrupados por ano.",
)
async def evolucao_sedentarismo(
    filters: QueryFilters = Depends(), db: AsyncSession = Depends(get_db)
):
    return await get_evolucao_sedentarismo(db, filters)


@router.get(
    "/evolucao/desfechos",
    response_model=List[EvolucaoDesfechosSaude],
    status_code=status.HTTP_200_OK,
    summary="Série Histórica: Desfechos de Saúde",
    description="Retorna a evolução histórica dos Desfechos de Saúde (Hipertensão, Diabetes, Depressão, IMC) agrupados por ano.",
)
async def evolucao_desfechos(filters: QueryFilters = Depends(), db: AsyncSession = Depends(get_db)):
    return await get_evolucao_desfechos(db, filters)


# ─── Endpoints de Análise Comparativa e Distribuição (LOD) ─────────────────────


@router.get(
    "/comparativo/sexo",
    response_model=ComparativoSexoResponse,
    status_code=status.HTTP_200_OK,
    summary="Comparativo por Sexo: Atividade Física",
    description="Retorna os indicadores de atividade física segmentados por sexo biológico (Masculino vs Feminino), mantendo os demais filtros globais.",
)
async def comparativo_sexo(filters: QueryFilters = Depends(), db: AsyncSession = Depends(get_db)):
    return await get_comparativo_sexo(db, filters)


@router.get(
    "/sedentarismo/faixa-etaria",
    response_model=List[SedentarismoFaixaEtariaItem],
    status_code=status.HTTP_200_OK,
    summary="Sedentarismo por Faixa Etária",
    description="Retorna indicadores de sedentarismo agrupados pelas 6 faixas etárias, permitindo avaliar a curva geracional de tempo de tela.",
)
async def sedentarismo_faixa_etaria(
    filters: QueryFilters = Depends(), db: AsyncSession = Depends(get_db)
):
    return await get_sedentarismo_faixa_etaria(db, filters)


@router.get(
    "/desfechos/cidades",
    response_model=List[RankingCidadeItem],
    status_code=status.HTTP_200_OK,
    summary="Ranking de Capitais: Desfechos de Saúde",
    description="Retorna o ranking ordenado de prevalência do agravo de saúde selecionado entre as 27 capitais brasileiras.",
)
async def desfechos_cidades(
    indicador: Literal["obesidade", "excesso_peso", "hipertensao", "diabetes", "depressao"] = Query(
        "obesidade",
        description="Indicador a rankear (obesidade, excesso_peso, hipertensao, diabetes, depressao)",
    ),
    filters: QueryFilters = Depends(),
    db: AsyncSession = Depends(get_db),
):
    return await get_desfechos_cidades(db, filters, indicador=indicador)


@router.get(
    "/dashboard",
    response_model=DashboardConsolidadoResponse,
    status_code=status.HTTP_200_OK,
    summary="Dashboard Consolidado (BFF)",
    description="Retorna em um único payload estruturado todos os blocos de dados necessários para alimentar o dashboard, reduzindo a sobrecarga de rede e o consumo de conexões.",
)
async def dashboard_consolidado(
    filters: QueryFilters = Depends(),
    indicador_ranking: Literal[
        "obesidade", "excesso_peso", "hipertensao", "diabetes", "depressao"
    ] = Query(
        "obesidade",
        description="Indicador a rankear na distribuição de capitais (obesidade, excesso_peso, hipertensao, diabetes, depressao)",
    ),
    db: AsyncSession = Depends(get_db),
):
    return await get_dashboard_consolidado(db, filters, indicador_ranking=indicador_ranking)
