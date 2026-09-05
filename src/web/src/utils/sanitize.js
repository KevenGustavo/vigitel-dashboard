/**
 * Utilitários de sanitização e segurança para o frontend VIGITEL
 */

/**
 * Escapa caracteres HTML perigosos para evitar XSS em templates dinâmicos e tooltips ECharts.
 * @param {string|number} input
 * @returns {string}
 */
export function escapeHtml(input) {
  if (input === null || input === undefined) return ''
  const str = String(input)
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  }
  return str.replace(/[&<>"'/]/g, (char) => map[char] || char)
}

/**
 * Formata com segurança um valor numérico para percentual com casas decimais fixas.
 * @param {number|string} val
 * @param {number} decimals
 * @returns {string}
 */
export function formatSafePercent(val, decimals = 1) {
  if (val === null || val === undefined || val === '') return '—'
  const num = Number(val)
  if (isNaN(num) || !isFinite(num)) return '—'
  return `${num.toFixed(decimals)}%`
}
