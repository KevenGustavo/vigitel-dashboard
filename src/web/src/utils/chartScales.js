/**
 * Utilitários de escala para gráficos epidemiológicos Apache ECharts.
 * 
 * Previne o truncamento e corte de linhas de evolução, barras e polígonos de radar
 * quando prevalências populacionais ultrapassam tetos estáticos (como 60%, 70% ou 80%),
 * preservando rigorosamente a linha de base em 0% e adicionando margem de respiro (headroom)
 * até o limite natural de 100%.
 */

/**
 * Calcula dinamicamente o teto (max) ideal para o eixo de prevalências percentuais (0 a 100%).
 *
 * @param {Object|number} value - Objeto provido pelo Apache ECharts `{ min: number, max: number }` ou valor numérico escalar de pico
 * @param {number} [defaultCeiling=80] - Teto padrão de conforto quando os valores estão dentro da faixa habitual
 * @param {number} [headroomMargin=5] - Margem percentual mínima de respiro acima do ponto máximo antes de expandir a escala
 * @returns {number} Valor máximo ideal para o eixo (múltiplo de 10, no mínimo defaultCeiling, no máximo 100)
 */
export function getAdaptivePrevalenceCeiling(value, defaultCeiling = 80, headroomMargin = 5) {
  // Extrai com segurança o pico numérico, tratando nulos, undefined, -Infinity ou NaN
  const peak = typeof value === 'number'
    ? value
    : (Number.isFinite(value?.max) ? value.max : 0)

  // Se não houver dados válidos ou pico for <= 0, mantém o teto padrão estável
  if (peak <= 0) {
    return defaultCeiling
  }

  const required = peak + headroomMargin

  // Se o pico com margem couber confortavelmente no teto padrão, preserva o padrão estável
  if (required <= defaultCeiling) {
    return defaultCeiling
  }

  // Caso contrário, expande suavemente para o próximo múltiplo de 10, limitado ao teto biológico de 100%
  const expanded = Math.ceil(required / 10) * 10
  return Math.min(100, Math.max(expanded, defaultCeiling))
}
