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
    filterOptions.value = response.data
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

    // Executa as 9 consultas da API em paralelo com cancelamento automático via signal
    const [
      resAtividade, resSedentarismo, resDesfechos,
      resEvoAtiv, resEvoSed, resEvoDesf,
      resCompSexo, resSedIdade, resRankCidades
    ] = await Promise.all([
      apiClient.get('/indicadores/atividade-fisica', { params, signal }),
      apiClient.get('/indicadores/sedentarismo', { params, signal }),
      apiClient.get('/indicadores/desfechos', { params, signal }),
      apiClient.get('/indicadores/evolucao/atividade-fisica', { params, signal }),
      apiClient.get('/indicadores/evolucao/sedentarismo', { params, signal }),
      apiClient.get('/indicadores/evolucao/desfechos', { params, signal }),
      apiClient.get('/indicadores/comparativo/sexo', { params, signal }),
      apiClient.get('/indicadores/sedentarismo/faixa-etaria', { params, signal }),
      apiClient.get('/indicadores/desfechos/cidades', {
        params: { ...params, indicador: indicadorRanking.value },
        signal
      })
    ])

    atividadeFisica.value = resAtividade.data
    sedentarismo.value = resSedentarismo.data
    desfechos.value = resDesfechos.data

    evolucaoAtividadeFisica.value = resEvoAtiv.data || []
    evolucaoSedentarismo.value = resEvoSed.data || []
    evolucaoDesfechos.value = resEvoDesf.data || []

    comparativoSexo.value = resCompSexo.data || null
    sedentarismoFaixaEtaria.value = resSedIdade.data || []
    rankingCidades.value = resRankCidades.data || []

    // Popula o objeto visaoGeral (Derived State com tendências calculadas)
    visaoGeral.value = {
      atinge_150min: {
        value: resAtividade.data?.atinge_150min,
        trend: calcTrend(resEvoAtiv.data, 'atinge_150min')
      },
      ativo_lazer: {
        value: resAtividade.data?.ativo_lazer,
        trend: calcTrend(resEvoAtiv.data, 'ativo_lazer')
      },
      tempo_tela_maior_3h: {
        value: resSedentarismo.data?.tempo_tela_maior_3h,
        trend: calcTrend(resEvoSed.data, 'tempo_tela_maior_3h')
      },
      obesidade: {
        value: resDesfechos.data?.obesidade,
        trend: calcTrend(resEvoDesf.data, 'obesidade')
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
