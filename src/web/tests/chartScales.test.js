import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import { getAdaptivePrevalenceCeiling } from '../src/utils/chartScales.js'

describe('Adaptive Prevalence Ceiling Tests (ECharts Scale)', () => {
  test('deve retornar defaultCeiling quando entrada for nula, indefinida ou inválida', () => {
    assert.equal(getAdaptivePrevalenceCeiling(null), 80)
    assert.equal(getAdaptivePrevalenceCeiling(undefined), 80)
    assert.equal(getAdaptivePrevalenceCeiling({}), 80)
    assert.equal(getAdaptivePrevalenceCeiling({ max: NaN }), 80)
    assert.equal(getAdaptivePrevalenceCeiling({ max: -Infinity }), 80)
    assert.equal(getAdaptivePrevalenceCeiling({ max: 0 }), 80)
    assert.equal(getAdaptivePrevalenceCeiling({ max: -10 }), 80)
    assert.equal(getAdaptivePrevalenceCeiling(null, 70), 70)
  })

  test('deve manter o teto padrão estável quando os dados estiverem na faixa habitual com folga', () => {
    // Pico 60% com defaultCeiling 80 -> 60 + 5 = 65 <= 80 -> 80
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 60 }), 80)
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 70 }), 80)
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 75 }), 80) // 75 + 5 = 80 <= 80 -> 80
  })

  test('deve expandir suavemente para 90% quando o pico se aproximar ou ultrapassar 80%', () => {
    // Pico 76% -> 76 + 5 = 81 -> ceil(81/10)*10 = 90
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 76 }), 90)
    // Dados reais do VIGITEL para Tempo de Tela 18-24 anos (81.89%, 83.95%)
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 81.89 }), 90)
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 83.95 }), 90)
    // 85% com margem de 5% = 90% -> cabe em 90
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 85 }), 90)
  })

  test('deve expandir para 100% quando o pico ultrapassar 85%', () => {
    // Pico 87% -> 87 + 5 = 92 -> ceil(92/10)*10 = 100
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 87 }), 100)
    // Dado real de Porto Alegre 18-24 anos em 2021 (90.96%)
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 90.96 }), 100)
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 95 }), 100)
  })

  test('nunca deve ultrapassar o limite absoluto de 100%', () => {
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 98 }), 100)
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 100 }), 100)
    assert.equal(getAdaptivePrevalenceCeiling({ min: 0, max: 105 }), 100)
  })

  test('deve aceitar números escalares diretamente (usado no Radar e Bar charts)', () => {
    assert.equal(getAdaptivePrevalenceCeiling(60), 80)
    assert.equal(getAdaptivePrevalenceCeiling(82), 90)
    assert.equal(getAdaptivePrevalenceCeiling(89), 100)
  })

  test('deve funcionar com tetos padrão customizados (ex: 60 para faixas etárias, 70 para atividade/desfechos)', () => {
    // Com defaultCeiling = 60
    assert.equal(getAdaptivePrevalenceCeiling(50, 60), 60)
    assert.equal(getAdaptivePrevalenceCeiling(55, 60), 60) // 55 + 5 = 60 <= 60 -> 60
    assert.equal(getAdaptivePrevalenceCeiling(58, 60), 70) // 58 + 5 = 63 -> 70
    assert.equal(getAdaptivePrevalenceCeiling(68, 60), 80) // 68 + 5 = 73 -> 80

    // Com defaultCeiling = 70 (ex: Desfechos onde excesso de peso atinge 76-78%)
    assert.equal(getAdaptivePrevalenceCeiling(60, 70), 70)
    assert.equal(getAdaptivePrevalenceCeiling(65, 70), 70)
    assert.equal(getAdaptivePrevalenceCeiling(70.52, 70), 80) // 70.52 + 5 = 75.52 -> 80
    assert.equal(getAdaptivePrevalenceCeiling(76.11, 70), 90) // 76.11 + 5 = 81.11 -> 90
    assert.equal(getAdaptivePrevalenceCeiling(78.17, 70), 90) // 78.17 + 5 = 83.17 -> 90
  })
})
