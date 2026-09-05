/**
 * Utilitários de Exportação de Dados Epidemiológicos — VIGITEL Monitor
 * Formatos otimizados para profissionais da saúde, epidemiologistas e pesquisadores
 */

const formatNum = (val, decimals = 1) => {
  if (val === null || val === undefined || isNaN(val)) return '—'
  return Number(val).toFixed(decimals).replace('.', ',')
}

const formatPct = (val, decimals = 1) => {
  if (val === null || val === undefined || isNaN(val)) return '—'
  return `${formatNum(val, decimals)}%`
}

const formatTrend = (trend) => {
  if (trend === null || trend === undefined) return 'Estável / Sem histórico'
  const val = Number(trend)
  const sinal = val > 0 ? '+' : ''
  const direcao = val > 0 ? '(Alta)' : val < 0 ? '(Queda)' : '(Estável)'
  return `${sinal}${val.toFixed(2).replace('.', ',')}% ${direcao}`
}

/**
 * Monta o bloco de metadados da consulta epidemiológica
 */
const buildMetadataSection = (filters) => {
  const dataExtracao = new Date().toLocaleString('pt-BR', { dateStyle: 'long', timeStyle: 'short' })
  const capitais = (!filters.capitais || filters.capitais.length === 0) 
    ? 'Todas as 27 capitais brasileiras' 
    : filters.capitais.join(', ')
  const idades = (!filters.faixa_etaria || filters.faixa_etaria.length === 0) ? 'Todas as faixas etárias' : filters.faixa_etaria.join(', ')
  const escolas = (!filters.escolaridade || filters.escolaridade.length === 0) ? 'Todos os níveis de escolaridade' : filters.escolaridade.join(', ')
  const racas = (!filters.raca_cor || filters.raca_cor.length === 0) ? 'Todas as categorias de raça/cor' : filters.raca_cor.join(', ')
  const sexo = filters.sexo || 'Ambos'

  return [
    '# ==============================================================================;',
    '# RELATÓRIO EPIDEMIOLÓGICO CONSOLIDADO — VIGITEL BRASIL;',
    '# Vigilância de Fatores de Risco e Proteção para Doenças Crônicas por Inquérito Telefônico;',
    '# Fonte: Ministério da Saúde do Brasil / Secretaria de Vigilância em Saúde (SVS);',
    '# ==============================================================================;',
    `# Data e Hora da Extração:;${dataExtracao}`,
    `# Período Histórico de Análise:;${filters.ano_inicio || 2006} a ${filters.ano_fim || 2024}`,
    `# Abrangência Geográfica:;${capitais}`,
    `# Recorte de Sexo Biológico:;${sexo}`,
    `# Faixas Etárias:;${idades}`,
    `# Escolaridade:;${escolas}`,
    `# Raça / Cor:;${racas}`,
    '# ==============================================================================;',
    ''
  ]
}

/**
 * 1. RELATÓRIO EPIDEMIOLÓGICO EM CSV (Formatado para Microsoft Excel / LibreOffice)
 * Contém BOM (\uFEFF) para codificação UTF-8 perfeita e delimitador ';' (padrão Brasil)
 */
export const generateEpidemiologicalCsv = (data, filters = {}) => {
  const lines = buildMetadataSection(filters)

  // --- SEÇÃO 1: INDICADORES PRINCIPAIS DE SAÚDE PÚBLICA ---
  lines.push('--- SEÇÃO 1: INDICADORES PRINCIPAIS DE SAÚDE PÚBLICA ---;')
  lines.push('Indicador;Domínio Epidemiológico;Prevalência Ponderada (%);Variação Recente (vs ano anterior);Classificação Clínica')

  const kpis = [
    {
      nome: 'Prática de Atividade Física (≥150 min/semana)',
      dominio: 'Atividade Física Global',
      val: data.visaoGeral?.atinge_150min?.value,
      trend: data.visaoGeral?.atinge_150min?.trend,
      classificacao: 'Fator de Proteção Cardiovascular'
    },
    {
      nome: 'Atividade Física no Tempo Livre / Lazer (≥150 min/sem)',
      dominio: 'Lazer e Recreação',
      val: data.visaoGeral?.ativo_lazer?.value,
      trend: data.visaoGeral?.ativo_lazer?.trend,
      classificacao: 'Fator de Proteção Cardiovascular'
    },
    {
      nome: 'Comportamento Sedentário Excessivo (>3h/dia de telas)',
      dominio: 'Sedentarismo',
      val: data.visaoGeral?.tempo_tela_maior_3h?.value,
      trend: data.visaoGeral?.tempo_tela_maior_3h?.trend,
      classificacao: 'Fator de Risco Crônico'
    },
    {
      nome: 'Obesidade Populacional (IMC ≥ 30 kg/m²)',
      dominio: 'Condição Nutricional / DCNT',
      val: data.visaoGeral?.obesidade?.value,
      trend: data.visaoGeral?.obesidade?.trend,
      classificacao: 'Desfecho Clínico Crônico'
    }
  ]

  kpis.forEach(k => {
    lines.push(`"${k.nome}";"${k.dominio}";${formatPct(k.val)};"${formatTrend(k.trend)}";"${k.classificacao}"`)
  })
  lines.push('')

  // --- SEÇÃO 2: DESFECHOS DE DOENÇAS CRÔNICAS NÃO TRANSMISSÍVEIS (DCNT) ---
  if (data.desfechos) {
    lines.push('--- SEÇÃO 2: DESFECHOS DE DOENÇAS CRÔNICAS NÃO TRANSMISSÍVEIS (DCNT) ---;')
    lines.push('Desfecho Clínico;Prevalência (%);Critério Diagnóstico Auto-referido')
    lines.push(`"Obesidade";${formatPct(data.desfechos.obesidade)};"Índice de Massa Corporal (IMC) ≥ 30 kg/m²"`)
    lines.push(`"Excesso de Peso (Sobrepeso + Obesidade)";${formatPct(data.desfechos.excesso_peso)};"Índice de Massa Corporal (IMC) ≥ 25 kg/m²"`)
    lines.push(`"Hipertensão Arterial Sistêmica";${formatPct(data.desfechos.hipertensao)};"Diagnóstico médico prévio de pressão alta"`)
    lines.push(`"Diabetes Mellitus";${formatPct(data.desfechos.diabetes)};"Diagnóstico médico prévio de diabetes"`)
    lines.push(`"Autoavaliação do Estado de Saúde como Ruim/Muito Ruim";${formatPct(data.desfechos.estado_saude_ruim)};"Percepção subjetiva de saúde desfavorável"`)
    lines.push('')
  }

  // --- SEÇÃO 3: DOMÍNIOS ESPECÍFICOS DE ATIVIDADE FÍSICA ---
  if (data.atividadeFisica) {
    lines.push('--- SEÇÃO 3: DOMÍNIOS ESPECÍFICOS DE ATIVIDADE FÍSICA ---;')
    lines.push('Domínio de Atividade;Prevalência (%);Definição Operacional')
    lines.push(`"Ativo no Lazer (≥150 min/sem)";${formatPct(data.atividadeFisica.ativo_lazer)};"Prática de esportes/exercícios em intensidade moderada/vigorosa"`)
    lines.push(`"Ativo no Deslocamento";${formatPct(data.atividadeFisica.ativo_deslocamento)};"Caminhada ou bicicleta no trajeto casa-trabalho/estudo ≥150 min/sem"`)
    lines.push(`"Ativo no Trabalho / Ocupacional";${formatPct(data.atividadeFisica.ativo_trabalho)};"Atividades pesadas ou caminhada intensa no expediente de trabalho"`)
    lines.push(`"Ativo nas Atividades Domésticas";${formatPct(data.atividadeFisica.ativo_domestico)};"Limpeza pesada ou tarefas do lar de grande esforço físico"`)
    lines.push(`"Inativo Fisicamente (Sedentário em todos os domínios)";${formatPct(data.atividadeFisica.inativo_total)};"Não atinge o mínimo recomendado em nenhum dos 4 domínios"`)
    lines.push('')
  }

  // --- SEÇÃO 4: COMPORTAMENTO SEDENTÁRIO ---
  if (data.sedentarismo) {
    lines.push('--- SEÇÃO 4: COMPORTAMENTO SEDENTÁRIO ---;')
    lines.push('Comportamento;Prevalência (%);Padrão de Exposição')
    lines.push(`"Tempo Excessivo de Telas Totais (>3h/dia)";${formatPct(data.sedentarismo.tempo_tela_maior_3h)};"Uso recreativo de TV, computador, tablet ou celular"`)
    lines.push(`"Tempo Excessivo Assistindo Televisão (>3h/dia)";${formatPct(data.sedentarismo.tempo_tv_maior_3h)};"Hábito de assistir TV por 3 horas ou mais ao dia"`)
    lines.push('')
  }

  // --- SEÇÃO 5: SÉRIE HISTÓRICA ANUAL CONSOLIDADA (EVOLUÇÃO TEMPORAL) ---
  const evoAtiv = data.evolucaoAtividadeFisica || []
  const evoSed = data.evolucaoSedentarismo || []
  const evoDesf = data.evolucaoDesfechos || []

  // Conjunto unificado de anos
  const allYears = Array.from(new Set([
    ...evoAtiv.map(d => d.ano),
    ...evoSed.map(d => d.ano),
    ...evoDesf.map(d => d.ano)
  ])).filter(Boolean).sort((a, b) => a - b)

  if (allYears.length > 0) {
    lines.push('--- SEÇÃO 5: SÉRIE HISTÓRICA ANUAL (EVOLUÇÃO TEMPORAL) ---;')
    lines.push('Ano;Ativ. Física Global (≥150 min);Ativo Lazer;Inativo Total;Telas >3h;TV >3h;Obesidade;Excesso Peso;Hipertensão;Diabetes')

    allYears.forEach(year => {
      const ativ = evoAtiv.find(d => d.ano === year) || {}
      const sed = evoSed.find(d => d.ano === year) || {}
      const desf = evoDesf.find(d => d.ano === year) || {}

      lines.push([
        year,
        formatPct(ativ.atinge_150min),
        formatPct(ativ.ativo_lazer),
        formatPct(ativ.inativo_total),
        formatPct(sed.tempo_tela_maior_3h),
        formatPct(sed.tempo_tv_maior_3h),
        formatPct(desf.obesidade),
        formatPct(desf.excesso_peso),
        formatPct(desf.hipertensao),
        formatPct(desf.diabetes)
      ].join(';'))
    })
    lines.push('')
  }

  // --- SEÇÃO 6: DISTRIBUIÇÃO POR FAIXA ETÁRIA (SEDENTARISMO) ---
  if (Array.isArray(data.sedentarismoFaixaEtaria) && data.sedentarismoFaixaEtaria.length > 0) {
    lines.push('--- SEÇÃO 6: DISTRIBUIÇÃO ETÁRIA DO SEDENTARISMO ---;')
    lines.push('Faixa Etária (anos);Tempo Telas Totais >3h (%);Tempo TV >3h (%)')
    data.sedentarismoFaixaEtaria.forEach(item => {
      lines.push(`"${item.faixa_etaria}";${formatPct(item.tempo_tela_maior_3h)};${formatPct(item.tempo_tv_maior_3h)}`)
    })
    lines.push('')
  }

  // --- SEÇÃO 7: COMPARATIVO POR SEXO BIOLÓGICO ---
  if (data.comparativoSexo?.masculino && data.comparativoSexo?.feminino) {
    lines.push('--- SEÇÃO 7: COMPARATIVO POR SEXO BIOLÓGICO ---;')
    lines.push('Domínio de Atividade;Masculino (%);Feminino (%)')
    const m = data.comparativoSexo.masculino
    const f = data.comparativoSexo.feminino
    lines.push(`"Atividade Física no Lazer";${formatPct(m.ativo_lazer)};${formatPct(f.ativo_lazer)}`)
    lines.push(`"Ativo no Deslocamento";${formatPct(m.ativo_deslocamento)};${formatPct(f.ativo_deslocamento)}`)
    lines.push(`"Ativo no Trabalho";${formatPct(m.ativo_trabalho)};${formatPct(f.ativo_trabalho)}`)
    lines.push(`"Ativo no Trabalho Doméstico";${formatPct(m.ativo_domestico)};${formatPct(f.ativo_domestico)}`)
    lines.push(`"Inatividade Física Total";${formatPct(m.inativo_total)};${formatPct(f.inativo_total)}`)
    lines.push('')
  }

  // --- SEÇÃO 8: RANKING DE CAPITAIS ---
  if (Array.isArray(data.rankingCidades) && data.rankingCidades.length > 0) {
    const indNome = data.indicadorRanking || 'Desfecho de Saúde'
    lines.push(`--- SEÇÃO 8: RANKING DE CAPITAIS BRASILEIRAS (${indNome.toUpperCase()}) ---;`)
    lines.push('Posição;Cidade;UF;Região;Prevalência (%)')
    data.rankingCidades.forEach((item, index) => {
      lines.push(`${index + 1};"${item.nome_cidade || item.cidade}";"${item.sigla_uf || ''}";"${item.regiao || ''}";${formatPct(item.valor)}`)
    })
  }

  // Prefix com UTF-8 Byte Order Mark (\uFEFF) para garantir abertura correta no Excel PT-BR
  return '\uFEFF' + lines.join('\r\n')
}

/**
 * 2. BASE DE DADOS TABULAR / TIDY FORMAT (CSV para R, Python, SPSS, Stata)
 * Estrutura plana (long format) onde cada linha é um registro analítico
 */
export const generateTidyDatasetCsv = (data, filters = {}) => {
  const rows = []
  rows.push('ano;indicador_id;indicador_rotulo;categoria;prevalencia_percentual;capitais_recorte;sexo_recorte;faixa_etaria_recorte;escolaridade_recorte;raca_cor_recorte')

  const capitaisStr = (!filters.capitais || filters.capitais.length === 0) ? 'Brasil (27 capitais)' : filters.capitais.join('|')
  const sexoStr = filters.sexo || 'Ambos'
  const idadeStr = (!filters.faixa_etaria || filters.faixa_etaria.length === 0) ? 'Todas' : filters.faixa_etaria.join('|')
  const escolaStr = (!filters.escolaridade || filters.escolaridade.length === 0) ? 'Todas' : filters.escolaridade.join('|')
  const racaStr = (!filters.raca_cor || filters.raca_cor.length === 0) ? 'Todas' : filters.raca_cor.join('|')

  const addPoint = (ano, id, rotulo, categoria, valor) => {
    if (valor === null || valor === undefined || isNaN(valor)) return
    rows.push([
      ano,
      `"${id}"`,
      `"${rotulo}"`,
      `"${categoria}"`,
      Number(valor).toFixed(2),
      `"${capitaisStr}"`,
      `"${sexoStr}"`,
      `"${idadeStr}"`,
      `"${escolaStr}"`,
      `"${racaStr}"`
    ].join(';'))
  }

  // Séries históricas
  ;(data.evolucaoAtividadeFisica || []).forEach(d => {
    if (!d.ano) return
    addPoint(d.ano, 'atinge_150min', 'Prática Recomendada Ativ. Física (≥150 min/sem)', 'Atividade Física', d.atinge_150min)
    addPoint(d.ano, 'ativo_lazer', 'Atividade Física no Lazer', 'Atividade Física', d.ativo_lazer)
    addPoint(d.ano, 'ativo_deslocamento', 'Ativo no Deslocamento', 'Atividade Física', d.ativo_deslocamento)
    addPoint(d.ano, 'ativo_trabalho', 'Ativo no Trabalho', 'Atividade Física', d.ativo_trabalho)
    addPoint(d.ano, 'ativo_domestico', 'Ativo nas Atividades Domésticas', 'Atividade Física', d.ativo_domestico)
    addPoint(d.ano, 'inativo_total', 'Inatividade Física Total', 'Atividade Física', d.inativo_total)
  })

  ;(data.evolucaoSedentarismo || []).forEach(d => {
    if (!d.ano) return
    addPoint(d.ano, 'tempo_tela_maior_3h', 'Tempo Excessivo de Telas Totais (>3h/dia)', 'Sedentarismo', d.tempo_tela_maior_3h)
    addPoint(d.ano, 'tempo_tv_maior_3h', 'Tempo Excessivo de Televisão (>3h/dia)', 'Sedentarismo', d.tempo_tv_maior_3h)
  })

  ;(data.evolucaoDesfechos || []).forEach(d => {
    if (!d.ano) return
    addPoint(d.ano, 'obesidade', 'Obesidade (IMC ≥ 30)', 'Desfecho DCNT', d.obesidade)
    addPoint(d.ano, 'excesso_peso', 'Excesso de Peso (IMC ≥ 25)', 'Desfecho DCNT', d.excesso_peso)
    addPoint(d.ano, 'hipertensao', 'Hipertensão Arterial Auto-referida', 'Desfecho DCNT', d.hipertensao)
    addPoint(d.ano, 'diabetes', 'Diabetes Mellitus Auto-referido', 'Desfecho DCNT', d.diabetes)
    addPoint(d.ano, 'estado_saude_ruim', 'Autoavaliação de Saúde Ruim/Muito Ruim', 'Desfecho DCNT', d.estado_saude_ruim)
  })

  return '\uFEFF' + rows.join('\r\n')
}

/**
 * 3. EXPORTAÇÃO COMPLETA EM JSON
 */
export const generateRawJson = (data, filters = {}) => {
  const payload = {
    sistema: 'VIGITEL Atividade Física e Saúde',
    gerado_em: new Date().toISOString(),
    filtros_ativos: {
      ano_inicio: filters.ano_inicio,
      ano_fim: filters.ano_fim,
      capitais: filters.capitais?.length > 0 ? filters.capitais : 'Todas as 27 capitais',
      sexo: filters.sexo || 'Ambos',
      faixa_etaria: filters.faixa_etaria?.length > 0 ? filters.faixa_etaria : 'Todas',
      escolaridade: filters.escolaridade?.length > 0 ? filters.escolaridade : 'Todas',
      raca_cor: filters.raca_cor?.length > 0 ? filters.raca_cor : 'Todas'
    },
    resumo_indicadores: data.visaoGeral || {},
    atividade_fisica: data.atividadeFisica || {},
    sedentarismo: data.sedentarismo || {},
    desfechos_prevalencia: data.desfechos || {},
    evolucao_historica: {
      atividade_fisica: data.evolucaoAtividadeFisica || [],
      sedentarismo: data.evolucaoSedentarismo || [],
      desfechos: data.evolucaoDesfechos || []
    },
    distribuicoes: {
      comparativo_sexo: data.comparativoSexo || null,
      sedentarismo_faixa_etaria: data.sedentarismoFaixaEtaria || [],
      ranking_capitais: data.rankingCidades || []
    }
  }

  return JSON.stringify(payload, null, 2)
}

/**
 * 4. DISPARADOR DE DOWNLOAD NO NAVEGADOR
 */
export const downloadFile = (content, filename, mimeType) => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
