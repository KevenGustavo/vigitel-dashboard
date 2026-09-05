import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import {
  calculateHealthIndex,
  getHealthIndexBreakdown,
  classifyHealthIndex,
  W_ATIVIDADE,
  W_SEDENTARISMO,
  W_OBESIDADE,
  HEALTH_INDEX_THRESHOLDS,
  HEALTH_INDEX_COLORS
} from '../src/features/visao-geral/utils/healthIndex.js'

describe('Epidemiological Health Index Calculation Tests', () => {

  test('constantes de faixas e cores epidemiológicas estão padronizadas', () => {
    assert.equal(HEALTH_INDEX_THRESHOLDS.FAVORABLE, 70)
    assert.equal(HEALTH_INDEX_THRESHOLDS.ATTENTION, 50)
    assert.equal(HEALTH_INDEX_COLORS.FAVORABLE, '#10B981')
    assert.equal(HEALTH_INDEX_COLORS.ATTENTION, '#F59E0B')
    assert.equal(HEALTH_INDEX_COLORS.CRITICAL, '#EF4444')
  })

  test('pesos ponderados somam exatamente 1.0 (100%)', () => {
    const totalWeight = Number((W_ATIVIDADE + W_SEDENTARISMO + W_OBESIDADE).toFixed(2))
    assert.equal(totalWeight, 1.0)
    assert.equal(W_OBESIDADE, 0.50)
    assert.equal(W_ATIVIDADE, 0.30)
    assert.equal(W_SEDENTARISMO, 0.20)
  })

  test('calcula índice corretamente com valores típicos do Brasil', () => {
    const index = calculateHealthIndex(36.5, 58.2, 22.4)
    assert.equal(index, 58.1)
  })

  test('decompõe a pontuação ponderada em parcelas exatas (Breakdown)', () => {
    const breakdown = getHealthIndexBreakdown(52.9, 62.5, 19.1)
    assert.ok(breakdown)
    assert.equal(breakdown.atividade.points, 15.9)
    assert.equal(breakdown.sedentarismo.points, 7.5)
    assert.equal(breakdown.obesidade.points, 40.5)
    assert.equal(breakdown.atividade.maxPoints, 30.0)
    assert.equal(breakdown.sedentarismo.maxPoints, 20.0)
    assert.equal(breakdown.obesidade.maxPoints, 50.0)
  })

  test('cenário ideal (100% ativos, 0% sedentarismo, 0% obesidade) resulta em 100 pontos', () => {
    const index = calculateHealthIndex(100, 0, 0)
    assert.equal(index, 100.0)
  })

  test('cenário crítico (0% ativos, 100% sedentarismo, 100% obesidade) resulta em 0 pontos', () => {
    const index = calculateHealthIndex(0, 100, 100)
    assert.equal(index, 0.0)
  })

  test('retorna null quando indicador essencial (atividade física ou obesidade) for nulo ou indefinido', () => {
    assert.equal(calculateHealthIndex(null, 50, 20), null)
    assert.equal(calculateHealthIndex(30, 50, null), null)
    assert.equal(calculateHealthIndex(undefined, 50, 20), null)
    assert.equal(calculateHealthIndex(30, 50, undefined), null)
    assert.equal(getHealthIndexBreakdown(null, 50, 20), null)
  })

  test('calcula índice adaptado para período pré-2016 quando sedentarismo for nulo ou indefinido', () => {
    // Exemplo: AF = 40%, Obesidade = 20%
    // Fórmula adaptada: (40 * 0.375) + ((100 - 20) * 0.625) = 15.0 + 50.0 = 65.0
    const adaptedIndexNull = calculateHealthIndex(40, null, 20)
    assert.equal(adaptedIndexNull, 65.0)

    const adaptedIndexUndef = calculateHealthIndex(40, undefined, 20)
    assert.equal(adaptedIndexUndef, 65.0)

    // Breakdown do modo adaptado pré-2016
    const breakdown = getHealthIndexBreakdown(40, null, 20)
    assert.ok(breakdown)
    assert.equal(breakdown.isAdapted, true)
    assert.equal(breakdown.total, 65.0)
    assert.equal(breakdown.atividade.weight, 37.5)
    assert.equal(breakdown.atividade.points, 15.0)
    assert.equal(breakdown.sedentarismo.isAvailable, false)
    assert.equal(breakdown.sedentarismo.points, 0)
    assert.equal(breakdown.obesidade.weight, 62.5)
    assert.equal(breakdown.obesidade.points, 50.0)
  })

  test('lida com entradas numéricas no formato string', () => {
    const index = calculateHealthIndex('40', '50', '20')
    assert.equal(index, 62.0)
  })

  test('classifica faixas epidemiológicas com terminologia clara de uma única palavra', () => {
    const favorable = classifyHealthIndex(75.5)
    assert.equal(favorable.status, 'favorable')
    assert.equal(favorable.label, 'Favorável')
    assert.equal(favorable.color, '#10B981')
    assert.equal(favorable.dotClass, 'bg-teal ring-teal/20')

    const intermediate = classifyHealthIndex(62.4)
    assert.equal(intermediate.status, 'intermediate')
    assert.equal(intermediate.label, 'Atenção')
    assert.equal(intermediate.color, '#F59E0B')
    assert.equal(intermediate.dotClass, 'bg-amber ring-amber/20')

    const concerning = classifyHealthIndex(45.0)
    assert.equal(concerning.status, 'concerning')
    assert.equal(concerning.label, 'Crítico')
    assert.equal(concerning.color, '#EF4444')
    assert.equal(concerning.dotClass, 'bg-red ring-red/20')

    const unknown = classifyHealthIndex(null)
    assert.equal(unknown.status, 'unknown')
    assert.equal(unknown.label, 'Indisponível')
    assert.equal(unknown.dotClass, 'bg-stone-400 ring-stone-200')
  })
})
