import { reactive, computed, watch } from 'vue'

const STORAGE_KEY = 'vigitel_filters_state'

const DEFAULT_STATE = {
  ano_inicio: 2006,
  ano_fim: 2024,
  capitais: [],
  sexo: 'Ambos',
  faixa_etaria: [],
  escolaridade: [],
  raca_cor: []
}

// Carrega estado inicial combinando URL Query Params > LocalStorage > Defaults
function loadInitialState() {
  if (typeof window === 'undefined') {
    return { ...DEFAULT_STATE }
  }

  const searchParams = new URLSearchParams(window.location.search)
  const hasUrlParams = searchParams.toString().length > 0

  if (hasUrlParams) {
    const loaded = { ...DEFAULT_STATE }
    
    if (searchParams.has('ano_inicio')) loaded.ano_inicio = parseInt(searchParams.get('ano_inicio')) || 2006
    if (searchParams.has('ano_fim')) loaded.ano_fim = parseInt(searchParams.get('ano_fim')) || 2024
    if (searchParams.has('cidade')) loaded.capitais = searchParams.getAll('cidade')
    if (searchParams.has('sexo')) loaded.sexo = searchParams.get('sexo') || 'Ambos'
    if (searchParams.has('faixa_etaria')) loaded.faixa_etaria = searchParams.getAll('faixa_etaria')
    if (searchParams.has('escolaridade')) loaded.escolaridade = searchParams.getAll('escolaridade')
    if (searchParams.has('raca_cor')) loaded.raca_cor = searchParams.getAll('raca_cor')

    return loaded
  }

  // Fallback para LocalStorage com validação estrita de segurança
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      const sanitizeStringArray = (arr) => Array.isArray(arr) ? arr.filter(item => typeof item === 'string' && item.length <= 100) : []
      const sanitizeYear = (val, fallback) => {
        const num = parseInt(val)
        return (!isNaN(num) && num >= 1990 && num <= 2050) ? num : fallback
      }

      return {
        ano_inicio: sanitizeYear(parsed.ano_inicio, DEFAULT_STATE.ano_inicio),
        ano_fim: sanitizeYear(parsed.ano_fim, DEFAULT_STATE.ano_fim),
        capitais: sanitizeStringArray(parsed.capitais),
        sexo: typeof parsed.sexo === 'string' ? parsed.sexo : DEFAULT_STATE.sexo,
        faixa_etaria: sanitizeStringArray(parsed.faixa_etaria),
        escolaridade: sanitizeStringArray(parsed.escolaridade),
        raca_cor: sanitizeStringArray(parsed.raca_cor)
      }
    }
  } catch (err) {
    if (import.meta.env.DEV) {
      console.warn('Erro ao recuperar filtros do localStorage:', err)
    }
  }

  return { ...DEFAULT_STATE }
}

// Estado global reativo (Shared State Pattern)
export const state = reactive(loadInitialState())

// Salva em localStorage e sincroniza a URL sem recarregar a página
function syncFiltersToStorageAndUrl() {
  if (typeof window === 'undefined') return

  const isDefault = (
    state.ano_inicio === DEFAULT_STATE.ano_inicio &&
    state.ano_fim === DEFAULT_STATE.ano_fim &&
    (!state.capitais || state.capitais.length === 0) &&
    state.sexo === DEFAULT_STATE.sexo &&
    (!state.faixa_etaria || state.faixa_etaria.length === 0) &&
    (!state.escolaridade || state.escolaridade.length === 0) &&
    (!state.raca_cor || state.raca_cor.length === 0)
  )

  if (isDefault) {
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch (e) {}
    window.history.replaceState({}, '', window.location.pathname)
    return
  }

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch (e) {
    console.warn('Erro ao salvar no localStorage:', e)
  }

  const params = new URLSearchParams()
  
  if (state.ano_inicio !== DEFAULT_STATE.ano_inicio) params.set('ano_inicio', state.ano_inicio)
  if (state.ano_fim !== DEFAULT_STATE.ano_fim) params.set('ano_fim', state.ano_fim)
  
  if (state.capitais && state.capitais.length > 0) {
    state.capitais.forEach(c => params.append('cidade', c))
  }

  if (state.sexo && state.sexo !== 'Ambos') {
    params.set('sexo', state.sexo)
  }

  if (state.faixa_etaria && state.faixa_etaria.length > 0) {
    state.faixa_etaria.forEach(f => params.append('faixa_etaria', f))
  }

  if (state.escolaridade && state.escolaridade.length > 0) {
    state.escolaridade.forEach(e => params.append('escolaridade', e))
  }

  if (state.raca_cor && state.raca_cor.length > 0) {
    state.raca_cor.forEach(r => params.append('raca_cor', r))
  }

  const newQuery = params.toString()
  const newUrl = newQuery ? `${window.location.pathname}?${newQuery}` : window.location.pathname
  window.history.replaceState({}, '', newUrl)
}

// Watcher global no nível de módulo para persistir mudanças automaticamente
watch(state, () => {
  syncFiltersToStorageAndUrl()
}, { deep: true })

export function useFilters() {
  // Retorna os parâmetros no formato esperado pela API FastAPI (removendo os nulos)
  const apiParams = computed(() => {
    const params = {}
    
    // Tratamento da faixa de anos
    let inicio = parseInt(state.ano_inicio)
    let fim = parseInt(state.ano_fim)

    // Corrige caso o usuário inverta a ordem
    if (inicio > fim) {
      const temp = inicio
      inicio = fim
      fim = temp
    }
    
    // Gera array com todos os anos na faixa para a API filtrar via .in_()
    const anos = []
    for (let y = inicio; y <= fim; y++) {
      anos.push(y)
    }
    params.ano = anos
    
    // Tratamento das capitais múltiplas
    if (state.capitais && state.capitais.length > 0) {
      params.cidade = state.capitais
    }

    if (state.sexo && state.sexo !== 'Ambos') params.sexo = state.sexo
    if (state.faixa_etaria && state.faixa_etaria.length > 0) params.faixa_etaria = state.faixa_etaria
    if (state.escolaridade && state.escolaridade.length > 0) params.escolaridade = state.escolaridade
    if (state.raca_cor && state.raca_cor.length > 0) params.raca_cor = state.raca_cor
    return params
  })

  const resetFilters = (minYear = 2006, maxYear = 2024) => {
    state.ano_inicio = minYear
    state.ano_fim = maxYear
    if (state.capitais) state.capitais.length = 0
    state.sexo = 'Ambos'
    if (state.faixa_etaria) state.faixa_etaria.length = 0
    if (state.escolaridade) state.escolaridade.length = 0
    if (state.raca_cor) state.raca_cor.length = 0

    if (typeof window !== 'undefined') {
      try {
        localStorage.removeItem(STORAGE_KEY)
      } catch (e) {}
      window.history.replaceState({}, '', window.location.pathname)
    }
  }

  return {
    state,
    apiParams,
    resetFilters
  }
}
