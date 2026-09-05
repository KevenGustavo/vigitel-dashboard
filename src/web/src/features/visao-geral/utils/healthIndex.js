/**
 * Utilitário de Cálculo do Índice de Saúde Populacional
 * Ponderação fundamentada na Fração Atribuível Populacional (PAF) do GBD 2021 (IHME/Lancet)
 * e nas metas do Plano de Ações Estratégicas para DCNT 2021-2030 (Ministério da Saúde).
 *
 * Pesos relativos padrão (período 2016-2023):
 * - Obesidade (IMC >= 30):          0.50 (50% - Maior PAF em DALYs por DCNTs no Brasil; fator de risco)
 * - Atividade Física (>= 150 min): 0.30 (30% - PAF direta ~3-5% sobre morbimortalidade; fator protetor)
 * - Excesso de Telas (>= 3h):      0.20 (20% - Fator de risco comportamental mediador independente)
 *
 * Pesos proporcionais adaptados para o período pré-2016 (sem coleta de telas no VIGITEL):
 * - Obesidade:        0.50 / 0.80 = 0.625 (62.5%)
 * - Atividade Física: 0.30 / 0.80 = 0.375 (37.5%)
 * - Total: 100%
 */

export const W_ATIVIDADE = 0.30
export const W_SEDENTARISMO = 0.20
export const W_OBESIDADE = 0.50

export const W_ATIVIDADE_PRE2016 = 0.375
export const W_OBESIDADE_PRE2016 = 0.625

export const HEALTH_INDEX_THRESHOLDS = {
  FAVORABLE: 70,
  ATTENTION: 50
}

export const HEALTH_INDEX_COLORS = {
  FAVORABLE: '#10B981',
  ATTENTION: '#F59E0B',
  CRITICAL: '#EF4444',
  MUTED: '#78716C'
}

/**
 * Calcula o Índice Sintético de Saúde Populacional (0 a 100 pontos).
 * Suporta cálculo completo de 3 eixos (pós-2016) e adaptação renormalizada de 2 eixos (pré-2016).
 *
 * @param {number|null} atinge150min - Prevalência de adultos que atingem >=150 min de AF
 * @param {number|null} tempoTelaMaior3h - Prevalência de adultos com excesso de telas (>=3h)
 * @param {number|null} obesidade - Prevalência de adultos com obesidade (IMC >= 30)
 * @returns {number|null} Pontuação de 0 a 100 ou null se AF ou Obesidade indisponíveis
 */
export function calculateHealthIndex(atinge150min, tempoTelaMaior3h, obesidade) {
  if (
    atinge150min === null || atinge150min === undefined ||
    obesidade === null || obesidade === undefined
  ) {
    return null
  }

  const af = Number(atinge150min)
  const ob = Number(obesidade)

  if (isNaN(af) || isNaN(ob)) {
    return null
  }

  // Caso 1: Período com coleta de sedentarismo (2016 em diante)
  if (tempoTelaMaior3h !== null && tempoTelaMaior3h !== undefined && !isNaN(Number(tempoTelaMaior3h))) {
    const sed = Number(tempoTelaMaior3h)
    const score = (af * W_ATIVIDADE) + ((100 - sed) * W_SEDENTARISMO) + ((100 - ob) * W_OBESIDADE)
    return Number(Math.max(0, Math.min(100, score)).toFixed(1))
  }

  // Caso 2: Período pré-2016 (tempo de tela não coletado no VIGITEL)
  // Renormalização proporcional dos pesos de AF (37.5%) e Obesidade (62.5%)
  const score = (af * W_ATIVIDADE_PRE2016) + ((100 - ob) * W_OBESIDADE_PRE2016)
  return Number(Math.max(0, Math.min(100, score)).toFixed(1))
}

/**
 * Decompõe a pontuação em parcelas ponderadas de cada indicador para máxima transparência didática.
 * @param {number|null} atinge150min
 * @param {number|null} tempoTelaMaior3h
 * @param {number|null} obesidade
 * @returns {object|null}
 */
export function getHealthIndexBreakdown(atinge150min, tempoTelaMaior3h, obesidade) {
  const total = calculateHealthIndex(atinge150min, tempoTelaMaior3h, obesidade)
  if (total === null) return null

  const af = Number(atinge150min)
  const ob = Number(obesidade)
  const hasSed = tempoTelaMaior3h !== null && tempoTelaMaior3h !== undefined && !isNaN(Number(tempoTelaMaior3h))

  if (hasSed) {
    const sed = Number(tempoTelaMaior3h)
    const afPoints = Number((af * W_ATIVIDADE).toFixed(1))
    const sedInverted = Number((100 - sed).toFixed(1))
    const sedPoints = Number((sedInverted * W_SEDENTARISMO).toFixed(1))
    const obInverted = Number((100 - ob).toFixed(1))
    const obPoints = Number((obInverted * W_OBESIDADE).toFixed(1))

    return {
      total,
      isAdapted: false,
      periodNote: null,
      atividade: {
        weight: 30,
        prevalence: af,
        points: afPoints,
        maxPoints: 30.0,
        formulaText: `${af.toFixed(1)}% × 0.30 = +${afPoints.toFixed(1)} pts`
      },
      sedentarismo: {
        weight: 20,
        prevalence: sed,
        invertedPrevalence: sedInverted,
        points: sedPoints,
        maxPoints: 20.0,
        isAvailable: true,
        formulaText: `(100 - ${sed.toFixed(1)}%) × 0.20 = +${sedPoints.toFixed(1)} pts`
      },
      obesidade: {
        weight: 50,
        prevalence: ob,
        invertedPrevalence: obInverted,
        points: obPoints,
        maxPoints: 50.0,
        formulaText: `(100 - ${ob.toFixed(1)}%) × 0.50 = +${obPoints.toFixed(1)} pts`
      }
    }
  }

  // Modo Adaptado (Pré-2016, sem coleta de sedentarismo)
  const afPoints = Number((af * W_ATIVIDADE_PRE2016).toFixed(1))
  const obInverted = Number((100 - ob).toFixed(1))
  const obPoints = Number((obInverted * W_OBESIDADE_PRE2016).toFixed(1))

  return {
    total,
    isAdapted: true,
    periodNote: 'Período pré-2016 (pesos renormalizados proporcionalmente sem coleta de telas)',
    atividade: {
      weight: 37.5,
      prevalence: af,
      points: afPoints,
      maxPoints: 37.5,
      formulaText: `${af.toFixed(1)}% × 0.375 = +${afPoints.toFixed(1)} pts`
    },
    sedentarismo: {
      weight: 0,
      prevalence: null,
      invertedPrevalence: null,
      points: 0,
      maxPoints: 0,
      isAvailable: false,
      formulaText: 'Variável de tempo de tela não era coletada no VIGITEL antes de 2016'
    },
    obesidade: {
      weight: 62.5,
      prevalence: ob,
      invertedPrevalence: obInverted,
      points: obPoints,
      maxPoints: 62.5,
      formulaText: `(100 - ${ob.toFixed(1)}%) × 0.625 = +${obPoints.toFixed(1)} pts`
    }
  }
}

/**
 * Classifica a pontuação em faixas epidemiológicas com nomenclatura de UMA PALAVRA e descrição detalhada no hover.
 * @param {number|null} score
 * @returns {{ label: string, status: string, color: string, badgeClass: string, textClass: string, description: string }}
 */
export function classifyHealthIndex(score) {
  if (score === null || score === undefined) {
    return {
      status: 'unknown',
      label: 'Indisponível',
      color: '#78716C',
      dotClass: 'bg-stone-400 ring-stone-200',
      badgeClass: 'bg-stone-100 text-stone-700 border-stone-200',
      textClass: 'text-stone-600',
      description: 'Aguardando dados dos indicadores para computar o índice epidemiológico.'
    }
  }

  if (score >= HEALTH_INDEX_THRESHOLDS.FAVORABLE) {
    return {
      status: 'favorable',
      label: 'Favorável',
      color: HEALTH_INDEX_COLORS.FAVORABLE,
      dotClass: 'bg-teal ring-teal/20',
      badgeClass: 'bg-teal/10 text-teal border-teal/20',
      textClass: 'text-teal',
      description: 'Nível adequado de proteção em saúde pública: elevada prática de atividade física associada a menor carga de sedentarismo e agravos crônicos, aproximando-se das metas do Plano DCNT 2021-2030.'
    }
  }

  if (score >= HEALTH_INDEX_THRESHOLDS.ATTENTION) {
    return {
      status: 'intermediate',
      label: 'Atenção',
      color: HEALTH_INDEX_COLORS.ATTENTION,
      dotClass: 'bg-amber ring-amber/20',
      badgeClass: 'bg-amber/10 text-amber border-amber/20',
      textClass: 'text-amber',
      description: 'Equilíbrio moderado que requer vigilância ativa: a população atinge patamares razoáveis de atividade física, porém o excesso de telas e a prevalência de obesidade acendem sinal de alerta para intervenções preventivas.'
    }
  }

  return {
    status: 'concerning',
    label: 'Crítico',
    color: HEALTH_INDEX_COLORS.CRITICAL,
    dotClass: 'bg-red ring-red/20',
    badgeClass: 'bg-red/10 text-red border-red/20',
    textClass: 'text-red',
    description: 'Cenário de alto risco à saúde pública: prevalência alarmante de fatores crônicos (sedentarismo e obesidade) combinada a níveis insuficientes de proteção física populacional.'
  }
}
