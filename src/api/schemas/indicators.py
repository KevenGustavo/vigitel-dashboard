from pydantic import BaseModel, Field
from typing import List, Optional

# ─── Indicadores Macro (KPIs) ──────────────────────────────────────────────────


class AtividadeFisicaResponse(BaseModel):
    """Resposta com o percentual de indivíduos fisicamente ativos por domínio e de inatividade geral."""

    ativo_lazer: Optional[float] = Field(None, description="Proporção de ativos no lazer (%)")
    ativo_deslocamento: Optional[float] = Field(
        None, description="Proporção de ativos no deslocamento para trabalho/escola (%)"
    )
    ativo_ocupacional: Optional[float] = Field(
        None, description="Proporção de ativos no trabalho (ocupacional) (%)"
    )
    ativo_domestico: Optional[float] = Field(
        None, description="Proporção de ativos no ambiente doméstico (%)"
    )
    inativo_total: Optional[float] = Field(
        None, description="Proporção da população fisicamente inativa globalmente (%)"
    )
    atinge_150min: Optional[float] = Field(
        None,
        description="Proporção da população que atinge a meta OMS de 150min/sem somando todos os domínios (%)",
    )


class SedentarismoResponse(BaseModel):
    """Resposta com o percentual do comportamento sedentário mapeado e segregado."""

    tempo_tela_maior_3h: Optional[float] = Field(
        None, description="Proporção total de indivíduos com >3h de tempo de tela (%)"
    )
    tempo_tv_maior_3h: Optional[float] = Field(
        None, description="Proporção de indivíduos com >3h de tempo em frente à TV (%)"
    )
    tempo_tela_exceto_tv_maior_3h: Optional[float] = Field(
        None,
        description="Proporção de indivíduos com >3h em outras telas como celular e tablet (%)",
    )


class DesfechosSaudeResponse(BaseModel):
    """Resposta com o percentual de agravos crônicos frequentemente correlacionados com o sedentarismo."""

    hipertensao: Optional[float] = Field(
        None, description="Prevalência de Hipertensão arterial (%)"
    )
    diabetes: Optional[float] = Field(None, description="Prevalência de Diabetes (%)")
    depressao: Optional[float] = Field(None, description="Prevalência de Depressão (%)")
    excesso_peso: Optional[float] = Field(
        None, description="Prevalência de Excesso de Peso (IMC >= 25) (%)"
    )
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


# ─── Estruturas Comparativas Demográficas e Geográficas (LOD) ─────────────────


class ComparativoSexoResponse(BaseModel):
    """Resposta com o perfil de atividade física segregado por sexo biológico."""

    masculino: Optional[AtividadeFisicaResponse] = Field(
        None, description="Indicadores para população masculina"
    )
    feminino: Optional[AtividadeFisicaResponse] = Field(
        None, description="Indicadores para população feminina"
    )


class SedentarismoFaixaEtariaItem(BaseModel):
    """Indicadores de sedentarismo para uma determinada faixa etária."""

    faixa_etaria: str = Field(..., description="Faixa etária (ex: '18-24', '65+')")
    tempo_tela_maior_3h: Optional[float] = Field(None, description="Tempo de tela total > 3h (%)")
    tempo_tv_maior_3h: Optional[float] = Field(None, description="Tempo de TV > 3h (%)")
    tempo_tela_exceto_tv_maior_3h: Optional[float] = Field(
        None, description="Tempo de telas digitais > 3h (%)"
    )


class RankingCidadeItem(BaseModel):
    """Prevalência de agravo de saúde para uma capital."""

    nome_cidade: str = Field(..., description="Nome da capital (ex: 'São Paulo')")
    valor: Optional[float] = Field(None, description="Prevalência percentual calculada (%)")


# ─── Envelope Consolidado de Dashboard (BFF) ──────────────────────────────────


class DashboardConsolidadoResponse(BaseModel):
    """Envelope consolidado com todos os blocos de dados para inicialização atômica do dashboard."""

    atividade_fisica: AtividadeFisicaResponse = Field(
        ..., description="KPIs consolidados de atividade física"
    )
    sedentarismo: SedentarismoResponse = Field(..., description="KPIs consolidados de sedentarismo")
    desfechos: DesfechosSaudeResponse = Field(
        ..., description="KPIs consolidados de desfechos de saúde"
    )
    evolucao_atividade_fisica: List[EvolucaoAtividadeFisica] = Field(
        default_factory=list, description="Série temporal de atividade física"
    )
    evolucao_sedentarismo: List[EvolucaoSedentarismo] = Field(
        default_factory=list, description="Série temporal de sedentarismo"
    )
    evolucao_desfechos: List[EvolucaoDesfechosSaude] = Field(
        default_factory=list, description="Série temporal de desfechos de saúde"
    )
    comparativo_sexo: ComparativoSexoResponse = Field(
        ..., description="Distribuição comparativa por sexo"
    )
    sedentarismo_faixa_etaria: List[SedentarismoFaixaEtariaItem] = Field(
        default_factory=list, description="Distribuição de sedentarismo por faixa etária"
    )
    ranking_cidades: List[RankingCidadeItem] = Field(
        default_factory=list, description="Ranking ordenado de capitais"
    )
