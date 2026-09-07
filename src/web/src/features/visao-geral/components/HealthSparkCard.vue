<template>
  <div
    class="bg-surface/80 hover:bg-card border border-border/80 rounded-xl p-2.5 sm:p-3 xl:p-3.5 transition-all duration-200 flex flex-col justify-between group shadow-2xs hover:shadow-xs active:scale-[0.99]"
    :class="borderAccentClass"
  >
    <!-- Topo Linha 1: Marcador de Eixo, Peso PAF, Pontos Contribuídos e Popover Informativo -->
    <div class="flex items-center justify-between gap-1 mb-1">
      <div class="flex items-center gap-1.5 min-w-0">
        <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: colorHex }"></span>
        <!-- Badge de Peso e Contribuição em Pontos -->
        <span
          v-if="isAvailable"
          class="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded border"
          :class="weightBadgeClass"
          :title="`Peso PAF: ${weight}% | Contribui com +${points} pts no score final`"
        >
          {{ weight }}% peso
        </span>
        <span
          v-else
          class="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded border bg-stone-100 text-stone-500 border-stone-200"
          title="Variável não coletada no período anterior a 2016"
        >
          Sem coleta pré-2016
        </span>
        <!-- Badge de Pontos Gerados para o Índice -->
        <span
          v-if="isAvailable && points !== null && points !== undefined"
          class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-stone-100 text-text-primary border border-stone-200/80"
          :title="formulaText || `Contribuição: +${points} pts`"
        >
          +{{ Number(points).toFixed(1) }} pts
        </span>
      </div>

      <!-- Botão/Popover Informativo Dark Stone (Hover/Touch) -->
      <div v-if="tooltipText" class="relative group/pop inline-flex items-center cursor-help shrink-0">
        <button
          type="button"
          @click.stop="toggleTooltip"
          class="text-text-muted hover:text-text-secondary p-0.5 rounded transition-colors focus:outline-hidden cursor-pointer active:scale-90"
          :aria-label="'Informações sobre ' + title"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
          </svg>
        </button>

        <!-- Dropdown Popover com z-index alto -->
        <div
          @click.stop
          class="absolute right-0 top-full mt-2 w-64 sm:w-68 max-w-[calc(100vw-32px)] p-3 bg-stone-900 text-stone-100 rounded-lg shadow-xl border border-stone-700 text-xs opacity-0 invisible group-hover/pop:opacity-100 group-hover/pop:visible transition-all duration-200 z-50 pointer-events-none text-left"
          :class="{ '!opacity-100 !visible !pointer-events-auto': isTooltipOpen }"
        >
          <div class="font-bold mb-1 text-[11px] uppercase tracking-wider font-display" :style="{ color: colorHex }">
            {{ tooltipTitle || title }}
          </div>
          <p class="leading-relaxed text-stone-200 text-[11px] font-sans">
            {{ tooltipText }}
          </p>
          <div v-if="formulaText" class="mt-2 p-1.5 rounded bg-stone-800/80 font-mono text-[10px]" :style="{ color: colorHex }">
            Cálculo: {{ formulaText }}
          </div>
          <div class="mt-2 pt-1.5 border-t border-stone-800 text-[10px] text-stone-400 flex items-center justify-between">
            <span>Classificação:</span>
            <span class="font-medium text-stone-300">{{ category }}</span>
          </div>
          <div class="w-2.5 h-2.5 bg-stone-900 border-t border-l border-stone-700 transform rotate-45 absolute -top-1.5 right-2"></div>
        </div>
      </div>
    </div>

    <!-- Topo Linha 2: Título Completo sem Truncamento -->
    <div class="mb-1">
      <h4 class="text-xs font-bold text-text-primary uppercase tracking-normal font-display whitespace-nowrap">
        {{ title }}
      </h4>
    </div>

    <!-- Centro: Valor Prevalente e Tendência -->
    <div class="mb-1.5 flex items-baseline justify-between gap-2">
      <!-- Valor Prevalente -->
      <div v-if="isLoading" class="h-7 w-20 bg-stone-200 animate-pulse rounded"></div>
      <div v-else-if="!isAvailable" class="flex items-baseline gap-1.5">
        <span class="text-xl sm:text-2xl xl:text-[26px] font-bold font-mono text-stone-400">—</span>
        <span class="text-[10px] text-stone-500 font-sans font-medium">{{ unavailableNotice }}</span>
      </div>
      <div v-else-if="value !== null && value !== undefined" class="flex items-baseline gap-1">
        <span class="text-xl sm:text-2xl xl:text-[26px] font-bold font-mono text-text-primary tracking-tight">
          {{ Number(value).toFixed(1) }}%
        </span>
        <span class="text-[11px] text-text-secondary font-sans font-normal">prev.</span>
      </div>
      <div v-else class="text-xs text-text-muted italic">Indisponível</div>

      <!-- Variação / Tendência -->
      <div v-if="!isLoading && isAvailable && trend !== null && trend !== undefined" class="flex items-center gap-1 text-[11px] font-mono font-medium" :class="trendColorClass">
        <!-- Ícone Seta para Cima -->
        <svg v-if="trend > 0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5 shrink-0">
          <path fill-rule="evenodd" d="M10 17a.75.75 0 01-.75-.75V5.612L5.29 9.77a.75.75 0 01-1.08-1.04l5.25-5.5a.75.75 0 011.08 0l5.25 5.5a.75.75 0 11-1.08 1.04l-3.96-4.158V16.25A.75.75 0 0110 17z" clip-rule="evenodd" />
        </svg>
        <!-- Ícone Seta para Baixo -->
        <svg v-else-if="trend < 0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5 shrink-0">
          <path fill-rule="evenodd" d="M10 3a.75.75 0 01.75.75v10.638l3.96-4.158a.75.75 0 111.08 1.04l-5.25 5.5a.75.75 0 01-1.08 0l-5.25-5.5a.75.75 0 111.08-1.04l3.96 4.158V3.75A.75.75 0 0110 3z" clip-rule="evenodd" />
        </svg>
        <!-- Ícone Estável -->
        <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5 shrink-0">
          <path fill-rule="evenodd" d="M4 10a.75.75 0 01.75-.75h10.5a.75.75 0 010 1.5H4.75A.75.75 0 014 10z" clip-rule="evenodd" />
        </svg>
        <span>{{ trend > 0 ? '+' : '' }}{{ Number(trend).toFixed(1) }} pp</span>
      </div>
    </div>

    <!-- Base: Mini-Sparkline ECharts -->
    <div class="h-9 sm:h-10 xl:h-11 2xl:h-12 w-full relative">
      <div v-if="isLoading" class="w-full h-full bg-stone-200/60 animate-pulse rounded"></div>
      <div v-else-if="!isAvailable" class="w-full h-full flex flex-col items-center justify-center text-[10px] text-stone-400 bg-stone-50/80 rounded border border-dashed border-stone-200 px-2 text-center">
        <span class="font-medium text-stone-500">Coleta iniciada em 2016</span>
        <span class="text-[9px] text-stone-400">Variável ausente no questionário anterior</span>
      </div>
      <v-chart
        v-else-if="sparklineData.length >= 2"
        :option="sparklineOption"
        autoresize
        class="w-full h-full"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-[10px] text-text-muted">
        Série histórica insuficiente
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTouchTooltip } from '../../core/composables/useTouchTooltip'

const { isOpen: isTooltipOpen, toggle: toggleTooltip } = useTouchTooltip()

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  category: {
    type: String,
    default: 'Fator Epidemiológico'
  },
  weight: {
    type: Number,
    required: true
  },
  points: {
    type: Number,
    default: null
  },
  maxPoints: {
    type: Number,
    default: null
  },
  formulaText: {
    type: String,
    default: ''
  },
  isAvailable: {
    type: Boolean,
    default: true
  },
  unavailableNotice: {
    type: String,
    default: 'Série iniciada em 2016'
  },
  value: {
    type: Number,
    default: null
  },
  trend: {
    type: Number,
    default: null
  },
  invertedTrend: {
    type: Boolean,
    default: false
  },
  color: {
    type: String,
    default: 'teal'
  },
  colorHex: {
    type: String,
    default: '#0D9488'
  },
  evolutionData: {
    type: Array,
    default: () => []
  },
  dataKey: {
    type: String,
    required: true
  },
  tooltipTitle: {
    type: String,
    default: ''
  },
  tooltipText: {
    type: String,
    default: ''
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

// Mapeamentos estáticos de classes (escopo de módulo para zero alocação em re-render)
const BORDER_ACCENT_MAP = {
  teal: 'hover:border-teal/60',
  amber: 'hover:border-amber/60',
  red: 'hover:border-red/60'
}

const WEIGHT_BADGE_MAP = {
  teal: 'bg-teal/10 text-teal border-teal/20',
  amber: 'bg-amber/10 text-amber border-amber/20',
  red: 'bg-red/10 text-red border-red/20'
}

// Mapeia classes visuais por tema de cor
const borderAccentClass = computed(() => BORDER_ACCENT_MAP[props.color] || 'hover:border-border-hover')
const weightBadgeClass = computed(() => WEIGHT_BADGE_MAP[props.color] || 'bg-stone-100 text-stone-700 border-stone-200')

// Cor da tendência
const trendColorClass = computed(() => {
  if (props.trend === 0 || props.trend === null || props.trend === undefined) {
    return 'text-text-secondary'
  }
  if (props.invertedTrend) {
    return props.trend > 0 ? 'text-red' : 'text-teal'
  }
  return props.trend > 0 ? 'text-teal' : 'text-red'
})

// Processa pontos ordenados para a mini-sparkline
const sparklineData = computed(() => {
  if (!Array.isArray(props.evolutionData) || props.evolutionData.length === 0) {
    return []
  }
  return [...props.evolutionData]
    .filter(item => item[props.dataKey] !== null && item[props.dataKey] !== undefined)
    .sort((a, b) => a.ano - b.ano)
})

// Constrói a opção compacta do ECharts Sparkline
const sparklineOption = computed(() => {
  const items = sparklineData.value
  if (items.length < 2) return {}

  const years = items.map(d => d.ano)
  const values = items.map(d => Number(d[props.dataKey]))

  const hex = props.colorHex

  return {
    grid: {
      top: 3,
      bottom: 3,
      left: 0,
      right: 0
    },
    xAxis: {
      type: 'category',
      show: false,
      data: years
    },
    yAxis: {
      type: 'value',
      show: false,
      min: (val) => Math.max(0, Math.floor(val.min - 1)),
      max: (val) => Math.ceil(val.max + 1)
    },
    tooltip: {
      trigger: 'axis',
      confine: true,
      backgroundColor: '#1C1917',
      borderColor: '#44403C',
      borderWidth: 1,
      padding: [4, 8],
      textStyle: {
        color: '#F5F5F4',
        fontSize: 10,
        fontFamily: 'Inter, sans-serif'
      },
      formatter: (params) => {
        if (!params || !params.length) return ''
        const p = params[0]
        return `<span style="color:#A8A29E">${p.name}:</span> <b>${Number(p.value).toFixed(1)}%</b>`
      }
    },
    series: [
      {
        type: 'line',
        data: values,
        smooth: 0.3,
        showSymbol: false,
        lineStyle: {
          width: 2,
          color: hex
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: hex + '44' },
              { offset: 1, color: hex + '05' }
            ]
          }
        },
        animationDuration: 800,
        animationEasing: 'cubicOut'
      }
    ]
  }
})
</script>
