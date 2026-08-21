from pydantic import BaseModel, Field
from typing import List, Optional

# ─── Indicadores Macro (KPIs) ──────────────────────────────────────────────────

class AtividadeFisicaResponse(BaseModel):
    """Resposta com o percentual de indivíduos fisicamente ativos por domínio e de inatividade geral."""
    ativo_lazer: Optional[float] = Field(None, description="Proporção de ativos no lazer (%)")
    ativo_deslocamento: Optional[float] = Field(None, description="Proporção de ativos no deslocamento para trabalho/escola (%)")
    ativo_ocupacional: Optional[float] = Field(None, description="Proporção de ativos no trabalho (ocupacional) (%)")
    ativo_domestico: Optional[float] = Field(None, description="Proporção de ativos no ambiente doméstico (%)")
    inativo_total: Optional[float] = Field(None, description="Proporção da população fisicamente inativa globalmente (%)")
    atinge_150min: Optional[float] = Field(None, description="Proporção da população que atinge a meta OMS de 150min/sem somando todos os domínios (%)")

class SedentarismoResponse(BaseModel):
    """Resposta com o percentual do comportamento sedentário mapeado e segregado."""
    tempo_tela_maior_3h: Optional[float] = Field(None, description="Proporção total de indivíduos com >3h de tempo de tela (%)")
    tempo_tv_maior_3h: Optional[float] = Field(None, description="Proporção de indivíduos com >3h de tempo em frente à TV (%)")
    tempo_tela_exceto_tv_maior_3h: Optional[float] = Field(None, description="Proporção de indivíduos com >3h em outras telas como celular e tablet (%)")

class DesfechosSaudeResponse(BaseModel):
    """Resposta com o percentual de agravos crônicos frequentemente correlacionados com o sedentarismo."""
    hipertensao: Optional[float] = Field(None, description="Prevalência de Hipertensão arterial (%)")
    diabetes: Optional[float] = Field(None, description="Prevalência de Diabetes (%)")
    depressao: Optional[float] = Field(None, description="Prevalência de Depressão (%)")
    excesso_peso: Optional[float] = Field(None, description="Prevalência de Excesso de Peso (IMC >= 25) (%)")
    obesidade: Optional[float] = Field(None, description="Prevalência de Obesidade (IMC >= 30) (%)")

# ─── Evolução Histórica (Time-Series) ──────────────────────────────────────────

class EvolucaoAtividadeFisica(AtividadeFisicaResponse):
    """Evolução temporal dos KPIs de Atividade Física."""
    ano: int = Field(..., description="Ano da coleta (ex: 2013)")

class EvolucaoSedentarismo(SedentarismoResponse):
    """Evolução temporal dos KPIs de Sedentarismo."""
    ano: int = Field(..., description="Ano da coleta (ex: 2013)")

class EvolucaoDesfechosSaude(DesfechosSaudeResponse):
    """Evolução temporal dos KPIs de Desfechos de Saúde."""
    ano: int = Field(..., description="Ano da coleta (ex: 2013)")

# ─── Análises Detalhadas (Séries e Agrupamentos) ───────────────────────────────

class DataPoint(BaseModel):
    """Ponto de dado genérico para gráficos de evolução ou agrupamento."""
    rotulo: str = Field(..., description="Eixo X (ex: '2019', 'São Paulo', '18-24 anos')")
    valor: float = Field(..., description="Percentual calculado (Eixo Y)")

class AnaliseDetalhadaResponse(BaseModel):
    """Estrutura padrão para qualquer análise agregada do painel interativo."""
    indicador: str = Field(..., description="Nome do indicador avaliado (ex: 'ativo_lazer')")
    dados: List[DataPoint] = Field(..., description="Lista de pontos para plotagem gráfica")
