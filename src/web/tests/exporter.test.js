import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import {
  generateEpidemiologicalCsv,
  generateTidyDatasetCsv,
  generateRawJson
} from '../src/utils/exporter.js'

describe('Epidemiological Exporter Tests', () => {
  const mockFilters = {
    ano_inicio: 2006,
    ano_fim: 2024,
    capitais: ['São Paulo', 'Rio de Janeiro'],
    sexo: 'Feminino',
    faixa_etaria: ['18-24', '25-34'],
    escolaridade: ['12 e mais'],
    raca_cor: ['Branca']
  }

  const mockData = {
    visaoGeral: {
      atinge_150min: { value: 38.5, trend: 1.2 },
      ativo_lazer: { value: 32.1, trend: 0.8 },
      tempo_tela_maior_3h: { value: 64.2, trend: -0.5 },
      obesidade: { value: 23.8, trend: 1.1 }
    },
    desfechos: {
      obesidade: 23.8,
      excesso_peso: 58.2,
      hipertensao: 27.4,
      diabetes: 9.1,
      estado_saude_ruim: 4.5
    },
    atividadeFisica: {
      atinge_150min: 38.5,
      ativo_lazer: 32.1,
      ativo_deslocamento: 14.2,
      ativo_trabalho: 11.5,
      ativo_domestico: 12.0,
      inativo_total: 13.8
    },
    sedentarismo: {
      tempo_tela_maior_3h: 64.2,
      tempo_tv_maior_3h: 24.1
    },
    evolucaoAtividadeFisica: [
      { ano: 2023, atinge_150min: 37.3, ativo_lazer: 31.3 },
      { ano: 2024, atinge_150min: 38.5, ativo_lazer: 32.1 }
    ],
    evolucaoSedentarismo: [
      { ano: 2023, tempo_tela_maior_3h: 64.7, tempo_tv_maior_3h: 25.0 },
      { ano: 2024, tempo_tela_maior_3h: 64.2, tempo_tv_maior_3h: 24.1 }
    ],
    evolucaoDesfechos: [
      { ano: 2023, obesidade: 22.7, excesso_peso: 57.5, hipertensao: 26.9, diabetes: 8.9 },
      { ano: 2024, obesidade: 23.8, excesso_peso: 58.2, hipertensao: 27.4, diabetes: 9.1 }
    ],
    sedentarismoFaixaEtaria: [
      { faixa_etaria: '18-24', tempo_tela_maior_3h: 80.5, tempo_tv_maior_3h: 22.0 },
      { faixa_etaria: '25-34', tempo_tela_maior_3h: 72.1, tempo_tv_maior_3h: 20.5 }
    ],
    rankingCidades: [
      { nome_cidade: 'Manaus', sigla_uf: 'AM', regiao: 'Norte', valor: 26.4 },
      { nome_cidade: 'Cuiabá', sigla_uf: 'MT', regiao: 'Centro-Oeste', valor: 25.8 }
    ],
    indicadorRanking: 'obesidade'
  }

  test('generateEpidemiologicalCsv deve incluir BOM UTF-8 e cabeçalho epidemiológico do SUS', () => {
    const csv = generateEpidemiologicalCsv(mockData, mockFilters)

    // Garante que o BOM está no início para compatibilidade perfeita com o Excel brasileiro
    assert.strictEqual(csv.charCodeAt(0), 0xFEFF, 'Deve começar com UTF-8 BOM')

    // Verifica metadados institucionais
    assert.ok(csv.includes('RELATÓRIO EPIDEMIOLÓGICO CONSOLIDADO — VIGITEL BRASIL'))
    assert.ok(csv.includes('Ministério da Saúde do Brasil'))
    assert.ok(csv.includes('São Paulo, Rio de Janeiro'))
    assert.ok(csv.includes('Feminino'))

    // Verifica seções clínicas
    assert.ok(csv.includes('--- SEÇÃO 1: INDICADORES PRINCIPAIS DE SAÚDE PÚBLICA ---'))
    assert.ok(csv.includes('Prática de Atividade Física (≥150 min/semana)'))
    assert.ok(csv.includes('38,5%'))
    assert.ok(csv.includes('+1,20% (Alta)'))

    assert.ok(csv.includes('--- SEÇÃO 2: DESFECHOS DE DOENÇAS CRÔNICAS NÃO TRANSMISSÍVEIS (DCNT) ---'))
    assert.ok(csv.includes('Hipertensão Arterial Sistêmica'))
    assert.ok(csv.includes('27,4%'))

    assert.ok(csv.includes('--- SEÇÃO 5: SÉRIE HISTÓRICA ANUAL (EVOLUÇÃO TEMPORAL) ---'))
    assert.ok(csv.includes('2024'))

    assert.ok(csv.includes('--- SEÇÃO 8: RANKING DE CAPITAIS BRASILEIRAS (OBESIDADE) ---'))
    assert.ok(csv.includes('Manaus'))
  })

  test('generateTidyDatasetCsv deve produzir formato tabular tidy para R / Python / SPSS', () => {
    const tidyCsv = generateTidyDatasetCsv(mockData, mockFilters)

    assert.strictEqual(tidyCsv.charCodeAt(0), 0xFEFF, 'Deve começar com UTF-8 BOM')
    assert.ok(tidyCsv.includes('ano;indicador_id;indicador_rotulo;categoria;prevalencia_percentual'))
    assert.ok(tidyCsv.includes('"atinge_150min"'))
    assert.ok(tidyCsv.includes('"Atividade Física"'))
    assert.ok(tidyCsv.includes('38.50'))
    assert.ok(tidyCsv.includes('"São Paulo|Rio de Janeiro"'))
    assert.ok(tidyCsv.includes('"Feminino"'))
  })

  test('generateRawJson deve produzir objeto serializável válido com filtros e dados', () => {
    const jsonStr = generateRawJson(mockData, mockFilters)
    const parsed = JSON.parse(jsonStr)

    assert.strictEqual(parsed.sistema, 'VIGITEL Atividade Física e Saúde')
    assert.strictEqual(parsed.filtros_ativos.sexo, 'Feminino')
    assert.strictEqual(parsed.resumo_indicadores.atinge_150min.value, 38.5)
    assert.strictEqual(parsed.desfechos_prevalencia.obesidade, 23.8)
    assert.strictEqual(parsed.distribuicoes.ranking_capitais.length, 2)
  })

  test('deve tratar graciosamente dados nulos ou vazios sem quebrar', () => {
    const emptyData = {}
    const emptyFilters = {}

    const csv = generateEpidemiologicalCsv(emptyData, emptyFilters)
    assert.ok(csv.includes('Todas as 27 capitais brasileiras'))
    assert.ok(csv.includes('—'))

    const tidy = generateTidyDatasetCsv(emptyData, emptyFilters)
    assert.ok(tidy.includes('ano;indicador_id;'))

    const jsonStr = generateRawJson(emptyData, emptyFilters)
    const parsed = JSON.parse(jsonStr)
    assert.strictEqual(parsed.filtros_ativos.capitais, 'Todas as 27 capitais')
  })
})
