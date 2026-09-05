from pydantic import BaseModel
from fastapi import Query
from typing import List, Optional

class FiltrosDisponiveis(BaseModel):
    """
    Modelo de resposta para o endpoint de filtros (/api/v1/filtros).
    Fornece as listas de opções para preencher os menus suspensos no frontend.
    """
    anos: List[int]
    cidades: List[dict]  # Ex: [{"nome_cidade": "São Paulo"}]
    faixas_etarias: List[str]
    escolaridades: List[str]
    sexos: List[str]
    racas_cores: List[str]

class QueryFilters:
    """
    Classe de Dependência (Dependency Injection) do FastAPI.
    Lida com a extração, conversão e validação dos parâmetros de URL (?ano=2023&cidade=sao paulo).
    """
    def __init__(
        self,
        ano: Optional[List[int]] = Query(None, description="Filtrar por anos específicos (múltiplos valores permitidos)"),
        cidade: Optional[List[str]] = Query(None, description="Filtrar pelo nome da cidade (ex: São Paulo, Rio de Janeiro)"),
        sexo: Optional[str] = Query(None, description="Filtrar por sexo (masculino ou feminino)"),
        faixa_etaria: Optional[List[str]] = Query(None, description="Filtrar por faixas etárias (ex: 18-24, 25-34)"),
        escolaridade: Optional[List[str]] = Query(None, description="Filtrar por faixas de escolaridade (ex: 0-8 anos, 12+ anos)"),
        raca_cor: Optional[List[str]] = Query(None, description="Filtrar por raça/cor declarada")
    ):
        self.ano = ano
        self.cidade = cidade
        self.sexo = sexo
        self.faixa_etaria = faixa_etaria
        self.escolaridade = escolaridade
        self.raca_cor = raca_cor
