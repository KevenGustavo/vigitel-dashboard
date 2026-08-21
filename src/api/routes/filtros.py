from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db.database import get_db
from src.api.schemas.filters import FiltrosDisponiveis
from src.api.services.filtros import get_filtros_disponiveis

router = APIRouter()

@router.get("", response_model=FiltrosDisponiveis, summary="Obter opções de filtros", description="Retorna os valores únicos (anos, cidades, etc.) disponíveis no banco de dados para popular os menus de filtro no frontend.")
async def get_filtros(db: AsyncSession = Depends(get_db)):
    return await get_filtros_disponiveis(db)
