import { ref, watch } from 'vue'
import apiClient from '../api/client'
import { useFilters } from './useFilters'

// ==============================================================================
// ESTADO GLOBAL COMPARTILHADO (MODULE-LEVEL SINGLETON PATTERN)
// Garante instância única em toda a aplicação, eliminando requisições duplicadas
// ==============================================================================

const isLoading = ref(false)
const isError = ref(false)

// Armazenamento dos dados dos indicadores
const visaoGeral = ref(null)
const atividadeFisica = ref(null)
const sedentarismo = ref(null)
const desfechos = ref(null)

// Séries temporais históricas
const evolucaoAtividadeFisica = ref([])
const evolucaoSedentarismo = ref([])
const evolucaoDesfechos = ref([])

// Análises comparativas e distribuições (LOD)
const comparativoSexo = ref(null)
const sedentarismoFaixaEtaria = ref([])
const rankingCidades = ref([])
const indicadorRanking = ref('obesidade')

// Opções de filtros para os dropdowns do cabeçalho
const filterOptions = ref(null)

// Controle de inicialização para disparo único
let isInitialized = false

// Controles de cancelamento de requisições pendentes (AbortController)
let activeAbortController = null
let activeRankingAbortController = null

// Timer de debounce para os filtros
let debounceTimer = null

const { apiParams } = useFilters()

// Função auxiliar para calcular tendência a partir da série histórica
const calcTrend = (evolucaoArray, key) => {
  if (!evolucaoArray) return null
  const validos = evolucaoArray.filter(item => item[key] !== null && item[key] !== undefined)
  if (validos.length < 2) return null
  
  const sorted = [...validos].sort((a, b) => a.ano - b.ano)
  const ultimo = sorted[sorted.length - 1]
  const penultimo = sorted[sorted.length - 2]
  
  return Number((ultimo[key] - penultimo[key]).toFixed(2))
}

// Busca o ranking de cidades para um indicador específico
const fetchRankingCidades = async (novoIndicador = null) => {
  if (novoIndicador) {
    indicadorRanking.value = novoIndicador
  }

  // Cancela busca anterior de ranking caso ainda esteja em voo
  if (activeRankingAbortController) {
    activeRankingAbortController.abort()
  }
  activeRankingAbortController = new AbortController()

  try {
    const res = await apiClient.get('/indicadores/desfechos/cidades', {
      params: {
        ...apiParams.value,
        indicador: indicadorRanking.value
      },
      signal: activeRankingAbortController.signal
    })
    rankingCidades.value = res.data || []
  } catch (err) {
    if (err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED') {
      return
    }
    console.error('Erro ao buscar ranking de cidades:', err)
  }
}

// Busca opções únicas para preencher os menus suspensos de filtro
const fetchFilterOptions = async () => {
  if (filterOptions.value) return // Já carregado
  try {
    const response = await apiClient.get('/filtros')
    const data = response.data
    // Garante ordenação pedagógica progressiva de escolaridade
    if (data?.escolaridades && Array.isArray(data.escolaridades)) {
      const order = {
        '0-8 anos': 1,
        '0 a 8 anos': 1,
        '9-11 anos': 2,
        '9 a 11 anos': 2,
        '12+ anos': 3,
        '12 anos ou mais': 3,
        '12 e mais': 3,
        'Não informado': 99
      }
      data.escolaridades.sort((a, b) => (order[a] || 50) - (order[b] || 50))
    }
    filterOptions.value = data
  } catch (error) {
    console.error('Erro ao buscar opções de filtros:', error)
  }
}

// Função principal de fetch que carrega todos os indicadores em paralelo
const fetchAllData = async () => {
  // Cancela a leva anterior de requisições caso ainda esteja em andamento
  if (activeAbortController) {
    activeAbortController.abort()
  }
  activeAbortController = new AbortController()
  const signal = activeAbortController.signal

  isLoading.value = true
  isError.value = false

  try {
    const params = apiParams.value

    // Executa uma única requisição ao endpoint consolidado (BFF), reduzindo em 89% as chamadas de rede
    const response = await apiClient.get('/indicadores/dashboard', {
      params: {
        ...params,
        indicador_ranking: indicadorRanking.value
      },
      signal
    })

    const data = response.data || {}

    atividadeFisica.value = data.atividade_fisica || null
    sedentarismo.value = data.sedentarismo || null
    desfechos.value = data.desfechos || null

    evolucaoAtividadeFisica.value = data.evolucao_atividade_fisica || []
    evolucaoSedentarismo.value = data.evolucao_sedentarismo || []
    evolucaoDesfechos.value = data.evolucao_desfechos || []

    comparativoSexo.value = data.comparativo_sexo || null
    sedentarismoFaixaEtaria.value = data.sedentarismo_faixa_etaria || []
    rankingCidades.value = data.ranking_cidades || []

    // Popula o objeto visaoGeral (Derived State com tendências calculadas)
    visaoGeral.value = {
      atinge_150min: {
        value: data.atividade_fisica?.atinge_150min,
        trend: calcTrend(data.evolucao_atividade_fisica, 'atinge_150min')
      },
      ativo_lazer: {
        value: data.atividade_fisica?.ativo_lazer,
        trend: calcTrend(data.evolucao_atividade_fisica, 'ativo_lazer')
      },
      tempo_tela_maior_3h: {
        value: data.sedentarismo?.tempo_tela_maior_3h,
        trend: calcTrend(data.evolucao_sedentarismo, 'tempo_tela_maior_3h')
      },
      obesidade: {
        value: data.desfechos?.obesidade,
        trend: calcTrend(data.evolucao_desfechos, 'obesidade')
      }
    }

    isLoading.value = false


  } catch (error) {
    if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED') {
      return // Cancelamento intencional para dar lugar à nova consulta
    }
    if (import.meta.env.DEV) {
      console.error('Erro ao buscar dados da API:', error)
    }
    isError.value = true
    isLoading.value = false
  }
}

// Watcher global centralizado com Debounce de 250ms
watch(apiParams, () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchAllData()
  }, 250)
}, { deep: true })

// Inicialização automática única (executada assim que qualquer componente solicitar)
const init = () => {
  if (isInitialized) return
  isInitialized = true
  fetchFilterOptions()
  fetchAllData()
}

export function useIndicadores() {
  // Dispara a carga na primeira montagem
  if (!isInitialized) {
    init()
  }

  return {
    isLoading,
    isError,
    visaoGeral,
    atividadeFisica,
    sedentarismo,
    desfechos,
    evolucaoAtividadeFisica,
    evolucaoSedentarismo,
    evolucaoDesfechos,
    comparativoSexo,
    sedentarismoFaixaEtaria,
    rankingCidades,
    indicadorRanking,
    fetchRankingCidades,
    filterOptions,
    fetchAllData,
    fetchFilterOptions
  }
}
