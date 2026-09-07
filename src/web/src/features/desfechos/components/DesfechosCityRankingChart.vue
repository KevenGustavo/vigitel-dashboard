<template>
  <div class="bg-card border border-border rounded-xl shadow-sm p-3.5 sm:p-4 xl:p-5 flex flex-col justify-between h-full relative">
    
    <!-- Topo: Cabeçalho com Layout em 2 Linhas Limpas -->
    <div class="pb-3 border-b border-border/60 space-y-2.5">
      
      <!-- Linha 1: Título Completo sem cortes + Badge Geográfico -->
      <div class="flex items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <div class="w-2.5 h-2.5 rounded-full shrink-0 shadow-xs" :class="currentOptionDotClass"></div>
          <h3 class="text-sm font-bold text-text-primary uppercase tracking-wide whitespace-nowrap font-display">
            Distribuição por Capitais
          </h3>
        </div>

        <!-- Badge Geográfico -->
        <span class="text-[10px] text-rose-700 bg-rose-50 border border-rose-200/80 px-2 py-0.5 rounded-md font-semibold shrink-0">
          27 Capitais
        </span>
      </div>

      <!-- Linha 2: Barra de Seleção com Custom Dropdown e Ícone Informativo com Hover -->
      <div class="flex items-center gap-2">
        
        <!-- Custom Dropdown em largura confortável -->
        <div class="relative flex-1" ref="dropdownRef">
          <button
            type="button"
            @click="isOpen = !isOpen"
            class="w-full inline-flex items-center justify-between gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold text-text-primary bg-stone-50 hover:bg-stone-100/90 border border-stone-200 shadow-2xs hover:border-stone-300 transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-stone-400/20"
          >
            <span class="flex items-center gap-2 truncate">
              <span class="w-2 h-2 rounded-full shrink-0 shadow-2xs" :class="currentOptionDotClass"></span>
              <span class="truncate">{{ currentOptionLabel }}</span>
            </span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-3.5 h-3.5 text-text-secondary transition-transform duration-200 shrink-0"
              :class="{ 'rotate-180': isOpen }"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
            </svg>
          </button>
          
          <!-- Menu Suspenso Flutuante -->
          <transition
            enter-active-class="transition duration-150 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-100 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0"
          >
            <div
              v-if="isOpen"
              class="absolute left-0 right-0 top-full mt-1.5 bg-card border border-border rounded-xl shadow-xl py-1 z-50 focus:outline-none"
            >
              <button
                v-for="opt in options"
                :key="opt.value"
                type="button"
                @click="selectOption(opt.value)"
                class="w-full text-left px-3 py-2 text-xs flex items-center justify-between transition-colors hover:bg-stone-100 cursor-pointer"
                :class="selectedIndicador === opt.value ? `${opt.activeText} font-bold ${opt.activeBg}` : 'text-text-secondary'"
              >
                <span class="flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full shrink-0 shadow-2xs" :class="opt.dotClass"></span>
                  <span>{{ opt.label }}</span>
                </span>
                <svg v-if="selectedIndicador === opt.value" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 shrink-0" :class="opt.activeText" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </transition>
        </div>

        <!-- Botão Informativo com Popover / Hover Explicativo (Hover/Touch) -->
        <div class="relative group/info shrink-0 cursor-help">
          <button
            type="button"
            @click.stop="toggleInfo"
            class="w-7 h-7 rounded-lg bg-stone-100 hover:bg-stone-200/80 active:scale-95 border border-stone-200 flex items-center justify-center text-text-secondary transition-colors shadow-2xs cursor-pointer"
            aria-label="Informações sobre o indicador ativo"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
            </svg>
          </button>

          <!-- Popover Explicativo da Variável Ativa -->
          <div
            @click.stop
            class="absolute right-0 top-full mt-2 w-72 max-w-[calc(100vw-32px)] p-3 bg-stone-900 text-stone-100 rounded-lg shadow-xl border border-stone-700 text-xs opacity-0 invisible group-hover/info:opacity-100 group-hover/info:visible transition-all duration-200 z-50 pointer-events-none"
            :class="{ '!opacity-100 !visible !pointer-events-auto': isInfoOpen }"
          >
            <div class="font-bold mb-1 text-[11px] uppercase tracking-wider flex items-center gap-1.5" :class="currentOptionTitleColor">
              <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="currentOptionDotClass"></span>
              <span>{{ currentOptionLabel }}</span>
            </div>
            <p class="leading-relaxed text-stone-200 text-[11px]">
              {{ currentIndicatorDescription }}
            </p>
            <div class="w-2.5 h-2.5 bg-stone-900 border-t border-l border-stone-700 transform rotate-45 absolute -top-1.5 right-2.5"></div>
          </div>
        </div>

      </div>
    </div>

    <!-- Centro: Lista Animada de Capitais com Vue TransitionGroup (FLIP Animation) -->
    <div class="relative w-full h-[280px] sm:h-[320px] xl:h-[360px] 2xl:h-[400px] my-2 overflow-y-auto pr-2 scrollbar-thin">
      <!-- Loading Skeleton -->
      <div v-if="isLoading" class="space-y-3 pt-2">
        <div v-for="i in 6" :key="i" class="space-y-1 animate-pulse">
          <div class="flex justify-between">
            <div class="h-3 bg-stone-200 rounded w-1/3"></div>
            <div class="h-3 bg-stone-200 rounded w-10"></div>
          </div>
          <div class="h-2.5 bg-stone-100 rounded-full w-full"></div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!rankingData.length" class="h-full flex flex-col justify-center items-center gap-2 text-center p-6">
        <p class="text-xs text-text-secondary">Dados indisponíveis para o recorte selecionado.</p>
      </div>

      <!-- TransitionGroup para Reordenação Fluida -->
      <TransitionGroup
        v-else
        name="rank-list"
        tag="div"
        class="space-y-1.5 relative"
      >
        <div
          v-for="(city, index) in rankingData"
          :key="city.nome_cidade"
          class="p-1.5 rounded-lg transition-colors hover:bg-stone-50 group"
          :class="{
            'bg-rose-50/80 border border-rose-200/80 shadow-2xs': isSelectedCity(city.nome_cidade)
          }"
        >
          <div class="flex items-center justify-between text-xs mb-1">
            <div class="flex items-center gap-2">
              <!-- Medalha / Posição -->
              <span
                class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 transition-colors duration-300"
                :class="getPositionBadgeClass(index)"
              >
                {{ index + 1 }}
              </span>
              <span 
                class="font-semibold text-text-primary group-hover:text-rose-600 transition-colors"
                :class="{ 'text-rose-700 font-bold': isSelectedCity(city.nome_cidade) }"
              >
                {{ city.nome_cidade }}
                <span v-if="isSelectedCity(city.nome_cidade)" class="text-[9.5px] font-normal text-rose-600 ml-1">(selecionada)</span>
              </span>
            </div>

            <!-- Valor Percentual -->
            <span class="font-bold text-text-primary font-mono text-xs">
              {{ city.valor !== null && city.valor !== undefined ? city.valor.toFixed(1) + '%' : '—' }}
            </span>
          </div>

          <!-- Barra de Progresso Relativa com Transição Fluida -->
          <div class="w-full h-2 bg-stone-100 rounded-full overflow-hidden flex items-center p-0.5 border border-stone-200/60 shadow-inner">
            <div
              class="h-full rounded-full transition-all duration-700 ease-out"
              :class="isSelectedCity(city.nome_cidade) ? currentOption.barColor : getBarColor(index)"
              :style="{ width: `${Math.min(Math.max((city.valor / maxVal) * 100, 2), 100)}%` }"
            ></div>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <!-- Rodapé: Limpo e Institucional -->
    <div class="pt-2.5 border-t border-border/40 text-[11px] text-text-muted flex items-center justify-between">
      <div class="flex items-center gap-1.5">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-rose-500 shrink-0" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
        </svg>
        <span>27 capitais brasileiras</span>
      </div>
      <span class="text-[10.5px] text-stone-400">Ordenação decrescente</span>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useFilters } from '../../core/composables/useFilters'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  currentIndicador: {
    type: String,
    default: 'obesidade'
  }
})

const emit = defineEmits(['change-indicador'])

const { state } = useFilters()
import { useTouchTooltip } from '../../core/composables/useTouchTooltip'

const { isOpen: isInfoOpen, toggle: toggleInfo } = useTouchTooltip()

const selectedIndicador = ref(props.currentIndicador)
const isOpen = ref(false)
const dropdownRef = ref(null)

watch(() => props.currentIndicador, (val) => {
  if (val) {
    selectedIndicador.value = val
  }
})

const options = [
  {
    value: 'obesidade',
    label: 'Obesidade',
    dotClass: 'bg-red-600',
    titleColor: 'text-rose-400',
    activeText: 'text-red-600',
    activeBg: 'bg-red-50/70',
    barColor: 'bg-red-600',
    barColorLight: 'bg-red-400'
  },
  {
    value: 'excesso_peso',
    label: 'Excesso de Peso',
    dotClass: 'bg-amber-500',
    titleColor: 'text-amber-400',
    activeText: 'text-amber-600',
    activeBg: 'bg-amber-50/70',
    barColor: 'bg-amber-500',
    barColorLight: 'bg-amber-400'
  },
  {
    value: 'hipertensao',
    label: 'Hipertensão',
    dotClass: 'bg-teal-600',
    titleColor: 'text-teal-400',
    activeText: 'text-teal-600',
    activeBg: 'bg-teal-50/70',
    barColor: 'bg-teal-600',
    barColorLight: 'bg-teal-400'
  },
  {
    value: 'diabetes',
    label: 'Diabetes',
    dotClass: 'bg-purple-600',
    titleColor: 'text-purple-400',
    activeText: 'text-purple-600',
    activeBg: 'bg-purple-50/70',
    barColor: 'bg-purple-600',
    barColorLight: 'bg-purple-400'
  },
  {
    value: 'depressao',
    label: 'Depressão',
    dotClass: 'bg-sky-600',
    titleColor: 'text-sky-400',
    activeText: 'text-sky-600',
    activeBg: 'bg-sky-50/70',
    barColor: 'bg-sky-600',
    barColorLight: 'bg-sky-400'
  }
]

const indicatorDescriptions = {
  obesidade: 'Proporção de adultos com Índice de Massa Corporal igual ou superior a 30 kg/m², calculada a partir de peso e altura autorreferidos.',
  excesso_peso: 'Proporção de adultos com Índice de Massa Corporal igual ou superior a 25 kg/m² (engloba sobrepeso e obesidade).',
  depressao: 'Proporção de adultos que relatam diagnóstico médico prévio de depressão.',
  hipertensao: 'Proporção de adultos que relatam diagnóstico médico prévio de hipertensão arterial sistêmica.',
  diabetes: 'Proporção de adultos que relatam diagnóstico médico prévio de diabetes mellitus.'
}

const currentOption = computed(() => {
  return options.find(o => o.value === selectedIndicador.value) || options[0]
})

const currentOptionLabel = computed(() => currentOption.value.label)
const currentOptionDotClass = computed(() => currentOption.value.dotClass)
const currentOptionTitleColor = computed(() => currentOption.value.titleColor)

const currentIndicatorDescription = computed(() => {
  return indicatorDescriptions[selectedIndicador.value] || 'Indicador de vigilância crônica do VIGITEL.'
})

const selectOption = (val) => {
  selectedIndicador.value = val
  isOpen.value = false
  emit('change-indicador', val)
}

// Fecha o dropdown ao clicar fora
const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const rankingData = computed(() => {
  return Array.isArray(props.data) ? props.data : []
})

const maxVal = computed(() => {
  if (!rankingData.value.length) return 100
  const max = Math.max(...rankingData.value.map(d => d.valor || 0))
  return max > 0 ? max * 1.15 : 100
})

const isSelectedCity = (cityName) => {
  if (!state || !state.capitais || !state.capitais.length) return false
  return state.capitais.includes(cityName)
}

const getPositionBadgeClass = (index) => {
  if (index === 0) return 'bg-amber-100 text-amber-800 border border-amber-300'
  if (index === 1) return 'bg-stone-200 text-stone-800 border border-stone-300'
  if (index === 2) return 'bg-orange-100 text-orange-800 border border-orange-300'
  return 'bg-stone-100 text-stone-600'
}

const getBarColor = (index) => {
  if (index < 3) return currentOption.value.barColor || 'bg-rose-500'
  if (index < 10) return currentOption.value.barColorLight || 'bg-rose-400'
  return 'bg-stone-400'
}
</script>

<style scoped>
/* Transição suave de reordenação com algoritmo FLIP do Vue */
.rank-list-move {
  transition: transform 0.55s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.rank-list-enter-active,
.rank-list-leave-active {
  transition: all 0.35s ease;
}

.rank-list-enter-from,
.rank-list-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.rank-list-leave-active {
  position: absolute;
}
</style>
