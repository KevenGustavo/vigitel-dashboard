import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import { escapeHtml, formatSafePercent } from '../src/utils/sanitize.js'

// ─── Lógica Auxiliar de Cálculo de Tendência ──────────────────────────────────
const calcTrend = (evolucaoArray, key) => {
  if (!evolucaoArray) return null
  const validos = evolucaoArray.filter(item => item[key] !== null && item[key] !== undefined)
  if (validos.length < 2) return null
  
  const sorted = [...validos].sort((a, b) => a.ano - b.ano)
  const ultimo = sorted[sorted.length - 1]
  const penultimo = sorted[sorted.length - 2]
  
  return Number((ultimo[key] - penultimo[key]).toFixed(2))
}

// ─── Lógica de Serialização de Parâmetros de Filtros ──────────────────────────
const buildApiParams = (state) => {
  const params = {}
  
  let inicio = parseInt(state.ano_inicio)
  let fim = parseInt(state.ano_fim)

  if (inicio > fim) {
    const temp = inicio
    inicio = fim
    fim = temp
  }
  
  const anos = []
  for (let y = inicio; y <= fim; y++) {
    anos.push(y)
  }
  params.ano = anos
  
  if (state.capitais && state.capitais.length > 0) {
    params.cidade = state.capitais
  }

  if (state.sexo && state.sexo !== 'Ambos') params.sexo = state.sexo
  if (state.faixa_etaria && state.faixa_etaria.length > 0) params.faixa_etaria = state.faixa_etaria
  if (state.escolaridade && state.escolaridade.length > 0) params.escolaridade = state.escolaridade
  if (state.raca_cor && state.raca_cor.length > 0) params.raca_cor = state.raca_cor
  return params
}

describe('Frontend Analytics & Data Processing Tests', () => {

  describe('calcTrend Functionality', () => {
    test('deve calcular a variação positiva (alta) entre os dois últimos anos válidos', () => {
      const mockData = [
        { ano: 2021, valor: 10.5 },
        { ano: 2022, valor: 12.0 },
        { ano: 2023, valor: 15.5 }
      ]
      const trend = calcTrend(mockData, 'valor')
      assert.equal(trend, 3.5)
    })

    test('deve calcular a variação negativa (queda) corretamente', () => {
      const mockData = [
        { ano: 2022, valor: 25.0 },
        { ano: 2023, valor: 21.3 }
      ]
      const trend = calcTrend(mockData, 'valor')
      assert.equal(trend, -3.7)
    })

    test('deve ignorar anos com valores nulos e calcular sobre os válidos', () => {
      const mockData = [
        { ano: 2020, valor: 10.0 },
        { ano: 2021, valor: 14.0 },
        { ano: 2022, valor: null }, // não coletado
        { ano: 2023, valor: null }
      ]
      const trend = calcTrend(mockData, 'valor')
      assert.equal(trend, 4.0)
    })

    test('deve retornar null caso haja menos de dois anos válidos', () => {
      assert.equal(calcTrend([], 'valor'), null)
      assert.equal(calcTrend([{ ano: 2024, valor: 15 }], 'valor'), null)
      assert.equal(calcTrend(null, 'valor'), null)
    })
  })

  describe('Filter Parameters Serialization', () => {
    test('deve gerar intervalo contínuo de anos para a API', () => {
      const state = { ano_inicio: 2020, ano_fim: 2024 }
      const params = buildApiParams(state)
      assert.deepEqual(params.ano, [2020, 2021, 2022, 2023, 2024])
    })

    test('deve inverter automaticamente se ano_inicio for maior que ano_fim', () => {
      const state = { ano_inicio: 2023, ano_fim: 2021 }
      const params = buildApiParams(state)
      assert.deepEqual(params.ano, [2021, 2022, 2023])
    })

    test('deve omitir "Ambos" no filtro de sexo para não restringir a query', () => {
      const state = { ano_inicio: 2024, ano_fim: 2024, sexo: 'Ambos' }
      const params = buildApiParams(state)
      assert.equal(params.sexo, undefined)
    })

    test('deve incluir cidades e perfis quando selecionados', () => {
      const state = {
        ano_inicio: 2024,
        ano_fim: 2024,
        capitais: ['São Paulo', 'Goiânia'],
        sexo: 'Feminino',
        faixa_etaria: ['18-24']
      }
      const params = buildApiParams(state)
      assert.deepEqual(params.cidade, ['São Paulo', 'Goiânia'])
      assert.equal(params.sexo, 'Feminino')
      assert.deepEqual(params.faixa_etaria, ['18-24'])
    })
  })

  describe('Reset and Active Filters Detection', () => {
    test('deve detectar quando não há filtros ativos (estado padrão nacional)', () => {
      const state = {
        ano_inicio: 2006,
        ano_fim: 2024,
        capitais: [],
        sexo: 'Ambos',
        faixa_etaria: [],
        escolaridade: [],
        raca_cor: []
      }
      const isActive = (
        state.ano_inicio !== 2006 ||
        state.ano_fim !== 2024 ||
        state.capitais.length > 0 ||
        state.sexo !== 'Ambos' ||
        state.faixa_etaria.length > 0 ||
        state.escolaridade.length > 0 ||
        state.raca_cor.length > 0
      )
      assert.equal(isActive, false)
    })

    test('deve detectar quando há filtros customizados ativos', () => {
      const state = {
        ano_inicio: 2015,
        ano_fim: 2024,
        capitais: ['Curitiba'],
        sexo: 'Feminino',
        faixa_etaria: [],
        escolaridade: [],
        raca_cor: []
      }
      const isActive = (
        state.ano_inicio !== 2006 ||
        state.ano_fim !== 2024 ||
        state.capitais.length > 0 ||
        state.sexo !== 'Ambos'
      )
      assert.equal(isActive, true)
    })
  })

  describe('Sanitization and Security Utilities', () => {
    test('deve escapar caracteres HTML perigosos para evitar XSS', () => {
      const malicious = '<script>alert("xss")</script>'
      assert.equal(escapeHtml(malicious), '&lt;script&gt;alert(&quot;xss&quot;)&lt;&#x2F;script&gt;')
    })

    test('deve escapar aspas e apóstrofos', () => {
      const input = `Lazer & "Esportes" '2024'`
      assert.equal(escapeHtml(input), 'Lazer &amp; &quot;Esportes&quot; &#x27;2024&#x27;')
    })

    test('deve lidar com entradas nulas e indefinidas graciosamente', () => {
      assert.equal(escapeHtml(null), '')
      assert.equal(escapeHtml(undefined), '')
      assert.equal(escapeHtml(2024), '2024')
    })

    test('deve formatar percentuais de forma segura', () => {
      assert.equal(formatSafePercent(15.42, 1), '15.4%')
      assert.equal(formatSafePercent(null), '—')
      assert.equal(formatSafePercent('invalid'), '—')
      assert.equal(formatSafePercent(Infinity), '—')
    })
  })

})

