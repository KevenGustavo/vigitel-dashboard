<template>
  <Teleport to="body">
    <!-- Backdrop com Fade -->
    <Transition
      enter-active-class="transition-opacity duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 bg-stone-900/60 backdrop-blur-xs"
        @click="close"
        aria-hidden="true"
      ></div>
    </Transition>

    <!-- Drawer / Bottom Sheet com Slide Up -->
    <Transition
      enter-active-class="transition-transform duration-300 ease-out"
      enter-from-class="translate-y-full"
      enter-to-class="translate-y-0"
      leave-active-class="transition-transform duration-200 ease-in"
      leave-from-class="translate-y-0"
      leave-to-class="translate-y-full"
    >
      <div
        v-if="isOpen"
        class="fixed inset-x-0 bottom-0 z-50 flex max-h-[90vh] flex-col rounded-t-2xl bg-white shadow-2xl border-t border-border overflow-hidden"
        role="dialog"
        aria-modal="true"
        aria-label="Filtros de Pesquisa Epidemiológica"
        @click.stop
      >
        <!-- Puxador Superior Tátil (Drag handle indicator) -->
        <div class="pt-2.5 pb-1 flex justify-center shrink-0 bg-stone-50 border-b border-border/50">
          <div class="w-12 h-1.5 rounded-full bg-stone-300"></div>
        </div>

        <!-- Cabeçalho do Drawer -->
        <div class="px-4 py-3 bg-stone-50 border-b border-border flex items-center justify-between shrink-0">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-lg bg-teal/15 text-teal flex items-center justify-center shrink-0">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-bold text-text-primary font-display leading-tight">Filtros de Pesquisa</h3>
              <p class="text-[11px] text-text-secondary">
                <span v-if="activeCount === 0">Padrão Nacional (sem filtros adicionais)</span>
                <span v-else class="text-teal font-semibold">{{ activeCount }} filtro(s) ativo(s)</span>
              </p>
            </div>
          </div>

          <button
            @click="close"
            class="w-8 h-8 rounded-full bg-stone-200/80 hover:bg-stone-300 text-stone-700 flex items-center justify-center transition-colors cursor-pointer"
            aria-label="Fechar filtros"
          >
            <svg class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>

        <!-- Conteúdo Rolável com as 6 Dimensões -->
        <div class="flex-1 overflow-y-auto px-4 py-4 space-y-4 text-left">
          
          <!-- 1. PERÍODO (ANOS) -->
          <div class="rounded-xl border border-border bg-stone-50/70 p-3.5 space-y-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5">
                <span class="text-xs font-bold uppercase tracking-wider text-text-primary font-display">1. Período</span>
              </div>
              <span class="text-xs font-bold text-teal bg-teal/10 px-2 py-0.5 rounded-md font-mono">
                {{ selectedMin }} a {{ selectedMax }}
              </span>
            </div>

            <!-- Slider Duplo -->
            <div class="relative h-1.5 w-full rounded-full bg-stone-200 mt-5 mb-4">
              <div 
                class="absolute h-full rounded-full bg-teal pointer-events-none"
                :style="{
                  left: `${((selectedMin - minYear) / (maxYear - minYear)) * 100}%`,
                  width: `${((selectedMax - selectedMin) / (maxYear - minYear)) * 100}%`
                }"
              ></div>
              <input 
                type="range" 
                :min="minYear" 
                :max="maxYear" 
                v-model.number="state.ano_inicio" 
                class="absolute -top-[5px] w-full appearance-none bg-transparent pointer-events-none custom-range outline-none"
              />
              <input 
                type="range" 
                :min="minYear" 
                :max="maxYear" 
                v-model.number="state.ano_fim" 
                class="absolute -top-[5px] w-full appearance-none bg-transparent pointer-events-none custom-range outline-none"
              />
            </div>

            <div class="flex justify-between text-[11px] font-semibold text-text-muted font-mono">
              <span>{{ minYear }}</span>
              <span>{{ maxYear }}</span>
            </div>
          </div>

          <!-- 2. CAPITAIS (27 CAPITAIS COM BUSCA E ACORDEÃO POR REGIÃO) -->
          <div class="rounded-xl border border-border bg-stone-50/70 p-3.5 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-wider text-text-primary font-display">2. Capitais</span>
              <button 
                type="button"
                @click="toggleAllCities" 
                class="text-[11px] font-bold text-teal hover:underline bg-teal/10 px-2 py-1 rounded-md transition-colors cursor-pointer"
              >
                {{ state.capitais.length > 0 ? 'Limpar Seleção' : 'Selecionar Todas' }}
              </button>
            </div>

            <!-- Campo de Busca de Capitais -->
            <div class="relative">
              <svg class="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-stone-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                v-model="citySearch"
                placeholder="Buscar capital pelo nome..."
                class="w-full pl-8 pr-3 py-1.5 text-xs bg-white border border-stone-200 rounded-lg text-text-primary placeholder:text-stone-400 focus:outline-none focus:border-teal focus:ring-1 focus:ring-teal/20"
              />
              <button
                v-if="citySearch"
                @click="citySearch = ''"
                class="absolute right-2.5 top-2 text-stone-400 hover:text-stone-600 text-xs"
              >
                ✕
              </button>
            </div>

            <!-- Agrupamento por Regiões -->
            <div class="space-y-2">
              <div
                v-for="(cidades, regiao) in filteredCidadesPorRegiao"
                :key="regiao"
                class="rounded-lg border border-stone-200 bg-white overflow-hidden"
              >
                <!-- Cabeçalho da Região -->
                <div 
                  @click="toggleRegionCollapse(regiao)"
                  class="px-3 py-2 bg-stone-100/70 flex items-center justify-between cursor-pointer select-none hover:bg-stone-100 transition-colors"
                >
                  <div class="flex items-center gap-2">
                    <svg 
                      class="w-3.5 h-3.5 text-stone-500 transition-transform duration-200"
                      :class="{ 'rotate-90': openRegions[regiao] }"
                      viewBox="0 0 20 20" fill="currentColor"
                    >
                      <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
                    </svg>
                    <span class="text-xs font-bold text-text-primary uppercase tracking-wider font-display">{{ regiao }}</span>
                    <span class="text-[10px] font-mono font-semibold px-1.5 py-0.2 bg-stone-200 text-stone-700 rounded-full">
                      {{ getSelectedCountInRegion(regiao) }}/{{ cidades.length }}
                    </span>
                  </div>

                  <button
                    type="button"
                    @click.stop="toggleRegion(regiao)"
                    class="text-[10px] font-bold text-teal hover:underline px-1.5 py-0.5"
                  >
                    {{ isRegionAllSelected(regiao) ? 'Desmarcar' : 'Marcar' }}
                  </button>
                </div>

                <!-- Lista de Cidades da Região (Expandível ou sempre aberta se houver busca) -->
                <div
                  v-show="openRegions[regiao] || citySearch.length > 0"
                  class="p-2.5 grid grid-cols-2 gap-1.5 border-t border-stone-100"
                >
                  <label
                    v-for="cidade in cidades"
                    :key="cidade.nome_cidade"
                    class="flex items-center gap-2 p-1.5 rounded-md hover:bg-stone-50 cursor-pointer min-h-[36px]"
                  >
                    <input
                      type="checkbox"
                      :checked="isCitySelected(cidade.nome_cidade)"
                      @change="toggleCity(cidade.nome_cidade)"
                      class="w-4 h-4 rounded border-stone-300 text-teal focus:ring-teal cursor-pointer accent-teal-600"
                    />
                    <span class="text-xs text-text-secondary leading-tight truncate font-sans">
                      {{ cidade.nome_cidade }}
                    </span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- 3. SEXO BIOLÓGICO -->
          <div class="rounded-xl border border-border bg-stone-50/70 p-3.5 space-y-2">
            <span class="text-xs font-bold uppercase tracking-wider text-text-primary font-display block">3. Sexo Biológico</span>
            <div class="grid grid-cols-3 gap-2">
              <button
                type="button"
                @click="state.sexo = 'Ambos'"
                class="py-2 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer text-center"
                :class="state.sexo === 'Ambos' ? 'bg-teal text-white shadow-xs font-bold' : 'bg-white border border-stone-200 text-text-secondary hover:bg-stone-100'"
              >
                Ambos
              </button>
              <button
                v-for="sexo in filterOptions?.sexos || ['Masculino', 'Feminino']"
                :key="sexo"
                type="button"
                @click="state.sexo = sexo"
                class="py-2 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer text-center"
                :class="state.sexo === sexo ? 'bg-teal text-white shadow-xs font-bold' : 'bg-white border border-stone-200 text-text-secondary hover:bg-stone-100'"
              >
                {{ sexo }}
              </button>
            </div>
          </div>

          <!-- 4. FAIXAS ETÁRIAS -->
          <div class="rounded-xl border border-border bg-stone-50/70 p-3.5 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-wider text-text-primary font-display">4. Faixas Etárias</span>
              <button
                type="button"
                @click="toggleAllOptions('faixa_etaria', filterOptions?.faixas_etarias)"
                class="text-[11px] font-bold text-teal hover:underline cursor-pointer"
              >
                {{ state.faixa_etaria.length > 0 ? 'Limpar' : 'Todas' }}
              </button>
            </div>
            <div class="grid grid-cols-2 gap-1.5">
              <label
                v-for="faixa in filterOptions?.faixas_etarias || []"
                :key="faixa"
                class="flex items-center gap-2 p-2 rounded-lg bg-white border border-stone-200 hover:bg-stone-50 cursor-pointer min-h-[38px]"
              >
                <input
                  type="checkbox"
                  :checked="state.faixa_etaria.includes(faixa)"
                  @change="toggleOption('faixa_etaria', faixa)"
                  class="w-4 h-4 rounded border-stone-300 text-teal focus:ring-teal cursor-pointer accent-teal-600"
                />
                <span class="text-xs text-text-secondary leading-tight">{{ faixa }}</span>
              </label>
            </div>
          </div>

          <!-- 5. ESCOLARIDADE -->
          <div class="rounded-xl border border-border bg-stone-50/70 p-3.5 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-wider text-text-primary font-display">5. Escolaridade</span>
              <button
                type="button"
                @click="toggleAllOptions('escolaridade', filterOptions?.escolaridades)"
                class="text-[11px] font-bold text-teal hover:underline cursor-pointer"
              >
                {{ state.escolaridade.length > 0 ? 'Limpar' : 'Todas' }}
              </button>
            </div>
            <div class="space-y-1.5">
              <label
                v-for="esc in filterOptions?.escolaridades || []"
                :key="esc"
                class="flex items-center gap-2 p-2 rounded-lg bg-white border border-stone-200 hover:bg-stone-50 cursor-pointer min-h-[38px]"
              >
                <input
                  type="checkbox"
                  :checked="state.escolaridade.includes(esc)"
                  @change="toggleOption('escolaridade', esc)"
                  class="w-4 h-4 rounded border-stone-300 text-teal focus:ring-teal cursor-pointer accent-teal-600"
                />
                <span class="text-xs text-text-secondary leading-tight">{{ esc }}</span>
              </label>
            </div>
          </div>

          <!-- 6. RAÇA / COR -->
          <div class="rounded-xl border border-border bg-stone-50/70 p-3.5 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-wider text-text-primary font-display">6. Raça / Cor</span>
              <button
                type="button"
                @click="toggleAllOptions('raca_cor', filterOptions?.racas_cores)"
                class="text-[11px] font-bold text-teal hover:underline cursor-pointer"
              >
                {{ state.raca_cor.length > 0 ? 'Limpar' : 'Todas' }}
              </button>
            </div>
            <div class="grid grid-cols-2 gap-1.5">
              <label
                v-for="raca in filterOptions?.racas_cores || []"
                :key="raca"
                class="flex items-center gap-2 p-2 rounded-lg bg-white border border-stone-200 hover:bg-stone-50 cursor-pointer min-h-[38px]"
              >
                <input
                  type="checkbox"
                  :checked="state.raca_cor.includes(raca)"
                  @change="toggleOption('raca_cor', raca)"
                  class="w-4 h-4 rounded border-stone-300 text-teal focus:ring-teal cursor-pointer accent-teal-600"
                />
                <span class="text-xs text-text-secondary leading-tight">{{ raca }}</span>
              </label>
            </div>
          </div>

        </div>

        <!-- Rodapé Fixo de Ação -->
        <div class="px-4 py-3 bg-white border-t border-border flex items-center gap-2.5 shrink-0">
          <button
            type="button"
            @click="handleClear"
            :disabled="!hasActiveFilters"
            class="flex-1 py-2.5 px-3 rounded-xl border text-xs font-bold transition-all cursor-pointer flex items-center justify-center gap-1.5"
            :class="hasActiveFilters 
              ? 'border-red-200 bg-red-50 text-red-600 hover:bg-red-100 hover:border-red-300' 
              : 'border-stone-200 bg-stone-50 text-stone-400 opacity-60 cursor-not-allowed'"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
            <span>Limpar Filtros</span>
          </button>

          <button
            type="button"
            @click="close"
            class="flex-2 py-2.5 px-4 rounded-xl bg-teal hover:bg-teal/90 text-white text-xs font-bold shadow-md shadow-teal/20 transition-all cursor-pointer flex items-center justify-center gap-2"
          >
            <svg class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            <span>Ver Resultados</span>
          </button>
        </div>

      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { useFilters } from '../../composables/useFilters'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  filterOptions: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:isOpen', 'close'])

const { state, resetFilters } = useFilters()

const close = () => {
  emit('update:isOpen', false)
  emit('close')
}

// Bloqueia a rolagem do body quando o drawer estiver aberto
watch(() => props.isOpen, (open) => {
  if (typeof document !== 'undefined') {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
  }
})

onUnmounted(() => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = ''
  }
})

// ─── 1. Período ───────────────────────────────────────
const minYear = computed(() => props.filterOptions?.anos ? Math.min(...props.filterOptions.anos) : 2006)
const maxYear = computed(() => props.filterOptions?.anos ? Math.max(...props.filterOptions.anos) : 2024)

const selectedMin = computed(() => Math.min(state.ano_inicio, state.ano_fim))
const selectedMax = computed(() => Math.max(state.ano_inicio, state.ano_fim))

// ─── 2. Capitais ──────────────────────────────────────
const REGION_MAPPING = {
  'Rio Branco': 'Norte', 'Macapá': 'Norte', 'Manaus': 'Norte', 'Belém': 'Norte', 'Porto Velho': 'Norte', 'Boa Vista': 'Norte', 'Palmas': 'Norte',
  'Maceió': 'Nordeste', 'Salvador': 'Nordeste', 'Fortaleza': 'Nordeste', 'São Luís': 'Nordeste', 'João Pessoa': 'Nordeste', 'Recife': 'Nordeste', 'Teresina': 'Nordeste', 'Natal': 'Nordeste', 'Aracaju': 'Nordeste',
  'Brasília': 'Centro-Oeste', 'Goiânia': 'Centro-Oeste', 'Cuiabá': 'Centro-Oeste', 'Campo Grande': 'Centro-Oeste',
  'Vitória': 'Sudeste', 'Belo Horizonte': 'Sudeste', 'São Paulo': 'Sudeste', 'Rio de Janeiro': 'Sudeste',
  'Curitiba': 'Sul', 'Porto Alegre': 'Sul', 'Florianópolis': 'Sul'
}

const citySearch = ref('')
const openRegions = reactive({
  'Norte': false,
  'Nordeste': false,
  'Centro-Oeste': false,
  'Sudeste': true,
  'Sul': false
})

const toggleRegionCollapse = (regiao) => {
  openRegions[regiao] = !openRegions[regiao]
}

const cidadesPorRegiao = computed(() => {
  const grupos = { 'Norte': [], 'Nordeste': [], 'Centro-Oeste': [], 'Sudeste': [], 'Sul': [] }
  if (props.filterOptions?.cidades) {
    props.filterOptions.cidades.forEach(c => {
      const regiao = REGION_MAPPING[c.nome_cidade] || 'Outros'
      if (grupos[regiao]) grupos[regiao].push(c)
    })
  }
  return grupos
})

const filteredCidadesPorRegiao = computed(() => {
  const search = citySearch.value.trim().toLowerCase()
  if (!search) return cidadesPorRegiao.value

  const filtrados = {}
  Object.keys(cidadesPorRegiao.value).forEach(reg => {
    const list = cidadesPorRegiao.value[reg].filter(c =>
      c.nome_cidade.toLowerCase().includes(search)
    )
    if (list.length > 0) {
      filtrados[reg] = list
    }
  })
  return filtrados
})

const isCitySelected = (nome_cidade) => state.capitais.includes(nome_cidade)

const toggleCity = (nome_cidade) => {
  const index = state.capitais.indexOf(nome_cidade)
  if (index === -1) {
    state.capitais.push(nome_cidade)
  } else {
    state.capitais.splice(index, 1)
  }
}

const isRegionAllSelected = (regiao) => {
  if (!cidadesPorRegiao.value[regiao]) return false
  const cidadesDaRegiao = cidadesPorRegiao.value[regiao].map(c => c.nome_cidade)
  if (cidadesDaRegiao.length === 0) return false
  return cidadesDaRegiao.every(id => state.capitais.includes(id))
}

const getSelectedCountInRegion = (regiao) => {
  if (!cidadesPorRegiao.value[regiao]) return 0
  return cidadesPorRegiao.value[regiao].filter(c => state.capitais.includes(c.nome_cidade)).length
}

const toggleRegion = (regiao) => {
  const cidadesDaRegiao = cidadesPorRegiao.value[regiao].map(c => c.nome_cidade)
  const allSelected = cidadesDaRegiao.every(id => state.capitais.includes(id))
  
  if (allSelected) {
    state.capitais = state.capitais.filter(id => !cidadesDaRegiao.includes(id))
  } else {
    cidadesDaRegiao.forEach(id => {
      if (!state.capitais.includes(id)) state.capitais.push(id)
    })
  }
}

const toggleAllCities = () => {
  if (state.capitais.length > 0) {
    state.capitais = []
  } else {
    state.capitais = props.filterOptions?.cidades?.map(c => c.nome_cidade) || []
  }
}

// ─── 4, 5, 6. Multiselects Genéricos ───────────────────
const toggleOption = (field, val) => {
  const current = state[field]
  const idx = current.indexOf(val)
  if (idx === -1) {
    current.push(val)
  } else {
    current.splice(idx, 1)
  }
}

const toggleAllOptions = (field, allOptions = []) => {
  if (!allOptions || allOptions.length === 0) return
  if (state[field].length > 0) {
    state[field] = []
  } else {
    state[field] = [...allOptions]
  }
}

// ─── Status Geral de Filtros ───────────────────────────
const hasActiveFilters = computed(() => {
  return (
    state.ano_inicio !== 2006 ||
    state.ano_fim !== 2024 ||
    (state.capitais && state.capitais.length > 0) ||
    (state.sexo && state.sexo !== 'Ambos') ||
    (state.faixa_etaria && state.faixa_etaria.length > 0) ||
    (state.escolaridade && state.escolaridade.length > 0) ||
    (state.raca_cor && state.raca_cor.length > 0)
  )
})

const activeCount = computed(() => {
  let count = 0
  if (state.ano_inicio !== 2006 || state.ano_fim !== 2024) count++
  if (state.capitais && state.capitais.length > 0) count++
  if (state.sexo && state.sexo !== 'Ambos') count++
  if (state.faixa_etaria && state.faixa_etaria.length > 0) count++
  if (state.escolaridade && state.escolaridade.length > 0) count++
  if (state.raca_cor && state.raca_cor.length > 0) count++
  return count
})

const handleClear = () => {
  resetFilters(minYear.value, maxYear.value)
}

// Listener para fechar no Escape
const handleKeyDown = (e) => {
  if (e.key === 'Escape' && props.isOpen) {
    close()
  }
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('keydown', handleKeyDown)
  }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('keydown', handleKeyDown)
  }
})
</script>

<style scoped>
.custom-range::-webkit-slider-thumb {
  pointer-events: auto;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: #14b8a6;
  border: 2px solid white;
  box-shadow: 0 1px 4px rgba(0,0,0,0.35);
  cursor: grab;
  position: relative;
  z-index: 10;
}
.custom-range::-webkit-slider-thumb:active {
  cursor: grabbing;
  transform: scale(1.15);
}
.custom-range::-moz-range-thumb {
  pointer-events: auto;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: #14b8a6;
  border: 2px solid white;
  box-shadow: 0 1px 4px rgba(0,0,0,0.35);
  cursor: grab;
  position: relative;
  z-index: 10;
}
.custom-range::-moz-range-thumb:active {
  cursor: grabbing;
  transform: scale(1.15);
}
</style>
