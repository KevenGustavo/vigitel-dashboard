<template>
  <div
    class="bg-card border border-border rounded-xl p-2.5 sm:p-3 xl:p-3.5 shadow-xs relative group/card hover:border-stone-300 transition-all hover:shadow-xs hover:z-30 active:scale-[0.99]"
    :class="extraClass"
  >
    <!-- Topo: Título da Variável + Trigger com Popover Informativo -->
    <div class="flex items-center justify-between text-xs text-text-secondary mb-1">
      <div class="flex items-center gap-1.5 min-w-0 pr-1">
        <span class="w-2 h-2 rounded-full shrink-0 shadow-2xs" :class="dotClass"></span>
        <span class="font-medium truncate font-display text-text-primary text-[11px] sm:text-xs xl:text-[13px]" :title="label">
          {{ label }}
        </span>
      </div>

      <!-- Botão / Trigger de Informação com Popover Hover/Touch -->
      <div class="relative group/info shrink-0 cursor-help">
        <button
          type="button"
          @click.stop="toggleTooltip"
          class="w-4.5 h-4.5 rounded-full bg-stone-100 hover:bg-stone-200/80 border border-stone-200/90 flex items-center justify-center text-text-secondary transition-colors shadow-2xs cursor-pointer active:scale-90"
          :aria-label="'Informações sobre ' + label"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-2.5 h-2.5 text-stone-500 group-hover/info:text-stone-700">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
          </svg>
        </button>

        <!-- Popover Informativo Flutuante (Dark Stone) -->
        <div
          @click.stop
          class="absolute top-full mt-2 w-64 sm:w-72 max-w-[calc(100vw-32px)] p-3 bg-stone-900 text-stone-100 rounded-lg shadow-xl border border-stone-700 text-xs opacity-0 invisible group-hover/info:opacity-100 group-hover/info:visible transition-all duration-200 z-50 pointer-events-none text-left"
          :class="[popoverPositionClass, { '!opacity-100 !visible !pointer-events-auto': isTooltipOpen }]"
        >
          <div class="font-bold mb-1 text-[11px] uppercase tracking-wider font-display flex items-center gap-1.5" :class="titleColor">
            <span class="w-1.5 h-1.5 rounded-full" :class="dotClass"></span>
            <span>{{ tooltipTitle || label }}</span>
          </div>
          <p class="leading-relaxed text-stone-200 text-[11px] font-sans whitespace-normal">
            {{ tooltipText }}
          </p>
          <div
            class="w-2.5 h-2.5 bg-stone-900 border-t border-l border-stone-700 transform rotate-45 absolute -top-1.5"
            :class="arrowPositionClass"
          ></div>
        </div>
      </div>
    </div>

    <!-- Meio: Valor Percentual -->
    <div class="text-lg xl:text-xl font-bold text-text-primary font-mono tracking-tight">
      <div v-if="isLoading" class="h-6 w-16 bg-stone-200 animate-pulse rounded my-0.5"></div>
      <span v-else>{{ formattedValue }}</span>
    </div>

    <!-- Base: Subtítulo Explicativo Curto -->
    <div class="text-[10px] xl:text-[11px] text-text-muted mt-0.5 truncate" :title="subtitle">
      {{ subtitle }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTouchTooltip } from '../../composables/useTouchTooltip'

const { isOpen: isTooltipOpen, toggle: toggleTooltip } = useTouchTooltip()

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    default: null
  },
  subtitle: {
    type: String,
    default: ''
  },
  dotClass: {
    type: String,
    default: 'bg-teal-600'
  },
  titleColor: {
    type: String,
    default: 'text-teal-400'
  },
  tooltipTitle: {
    type: String,
    default: ''
  },
  tooltipText: {
    type: String,
    default: ''
  },
  align: {
    type: String,
    default: 'left', // 'left' | 'right' | 'responsive'
    validator: (val) => ['left', 'right', 'responsive'].includes(val)
  },
  extraClass: {
    type: String,
    default: ''
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

// Formatação do valor numérico
const formattedValue = computed(() => {
  if (props.value === null || props.value === undefined) {
    return '—'
  }
  const num = Number(props.value)
  return isNaN(num) ? String(props.value) : `${num.toFixed(1)}%`
})

// Classe de alinhamento do popover
const popoverPositionClass = computed(() => {
  if (props.align === 'right') {
    return 'right-0'
  }
  if (props.align === 'responsive') {
    return 'left-0 sm:left-auto sm:right-0 lg:left-0'
  }
  return 'left-0'
})

// Classe da seta do popover
const arrowPositionClass = computed(() => {
  if (props.align === 'right') {
    return 'right-2'
  }
  if (props.align === 'responsive') {
    return 'left-2 sm:left-auto sm:right-2 lg:left-2 lg:right-auto'
  }
  return 'left-2'
})
</script>
