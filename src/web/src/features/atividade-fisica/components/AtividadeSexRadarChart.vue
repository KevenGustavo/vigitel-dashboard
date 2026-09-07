<template>
  <div class="bg-card border border-border rounded-xl shadow-sm p-3.5 sm:p-4 xl:p-5 flex flex-col justify-between h-full relative">
    
    <!-- Topo: Cabeçalho do Card -->
    <div class="pb-2 border-b border-border/60">
      <div class="flex items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <div class="w-2.5 h-2.5 rounded-full bg-teal"></div>
          <h3 class="text-sm font-bold text-text-primary uppercase tracking-wide font-display">
            Comparativo por Sexo
          </h3>
        </div>

        <!-- Badge Explicativo LOD (Hover/Touch) -->
        <div class="relative group/lod inline-flex items-center cursor-help">
          <button
            type="button"
            @click.stop="toggleLod"
            class="text-[10.5px] text-text-secondary bg-stone-100 hover:bg-stone-200/80 active:scale-95 border border-stone-200/80 px-2 py-0.5 rounded-md font-medium transition-colors flex items-center gap-1 cursor-pointer"
            aria-label="Informações sobre o comparativo intergênero"
          >
            <span>Intergênero</span>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5 text-stone-400">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
            </svg>
          </button>

          <!-- Popover Explicativo LOD -->
          <div
            @click.stop
            class="absolute right-0 top-full mt-2 w-72 max-w-[calc(100vw-32px)] p-3 bg-stone-900 text-stone-100 rounded-lg shadow-xl border border-stone-700 text-xs opacity-0 invisible group-hover/lod:opacity-100 group-hover/lod:visible transition-all duration-200 z-50 pointer-events-none text-left"
            :class="{ '!opacity-100 !visible !pointer-events-auto': isLodOpen }"
          >
            <div class="font-bold text-teal-400 mb-1 text-[11px] uppercase tracking-wider">
              Comparativo Intergênero
            </div>
            <p class="leading-relaxed text-stone-200 text-[11px]">
              Prevalência (%) nos 5 domínios de atividade física contrastando homens e mulheres. Mantém ativos todos os demais filtros (ano, cidade, idade e escolaridade).
            </p>
            <div class="w-2.5 h-2.5 bg-stone-900 border-t border-l border-stone-700 transform rotate-45 absolute -top-1.5 right-6"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Centro: Gráfico Radar do ECharts -->
    <div class="relative w-full h-[290px] sm:h-[330px] xl:h-[370px] 2xl:h-[410px] my-1">
      <!-- Loading Skeleton -->
      <div v-if="isLoading" class="absolute inset-0 z-10 bg-card">
        <ChartSkeleton type="radar" />
      </div>

      <!-- Empty State -->
      <div v-else-if="!hasData" class="absolute inset-0 flex flex-col justify-center items-center gap-2 text-center p-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-stone-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        <p class="text-sm font-semibold text-text-primary">Dados de sexo indisponíveis</p>
        <p class="text-xs text-text-secondary">Tente ajustar os filtros globais.</p>
      </div>

      <!-- ECharts Radar Component -->
      <v-chart
        v-else
        class="w-full h-full"
        :option="chartOption"
        autoresize
      />
    </div>

    <!-- Rodapé: Resumo e Destaque Epidemiológico -->
    <div class="pt-2 border-t border-border/40 text-[11px] text-text-muted flex flex-col gap-1">
      <div class="flex items-center justify-between text-xs">
        <div class="flex items-center gap-3">
          <span class="flex items-center gap-1 text-blue-600 font-semibold">
            <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Masculino
          </span>
          <span class="flex items-center gap-1 text-pink-600 font-semibold">
            <span class="w-2.5 h-2.5 rounded-full bg-pink-500"></span> Feminino
          </span>
        </div>
        <span class="text-[10px] text-stone-400">Escala de 0 a 70%</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import ChartSkeleton from '../../core/components/ui/ChartSkeleton.vue'
import { escapeHtml } from '../../../utils/sanitize'
import { getAdaptivePrevalenceCeiling } from '../../../utils/chartScales'
import { useTouchTooltip } from '../../core/composables/useTouchTooltip'

const { isOpen: isLodOpen, toggle: toggleLod } = useTouchTooltip()

const props = defineProps({
  data: {
    type: Object,
    default: () => null
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const hasData = computed(() => {
  return props.data && (props.data.masculino || props.data.feminino)
})

const chartOption = computed(() => {
  if (!hasData.value) return {}

  const masc = props.data.masculino || {}
  const fem = props.data.feminino || {}

  const mascValues = [
    masc.ativo_lazer || 0,
    masc.ativo_ocupacional || 0,
    masc.ativo_deslocamento || 0,
    masc.ativo_domestico || 0,
    masc.atinge_150min || 0
  ]

  const femValues = [
    fem.ativo_lazer || 0,
    fem.ativo_ocupacional || 0,
    fem.ativo_deslocamento || 0,
    fem.ativo_domestico || 0,
    fem.atinge_150min || 0
  ]

  const allVals = [...mascValues, ...femValues]
  const peak = Math.max(...allVals, 0)
  const radarMax = getAdaptivePrevalenceCeiling(peak, 70)

  return {
    tooltip: {
      trigger: 'item',
      confine: true,
      backgroundColor: 'rgba(255, 255, 255, 0.98)',
      borderColor: '#E2E8F0',
      borderWidth: 1,
      padding: [10, 14],
      textStyle: {
        color: '#1C1917',
        fontSize: 12
      },
      formatter: (params) => {
        const isMasc = params.name === 'Masculino'
        const color = isMasc ? '#3B82F6' : '#EC4899'
        const vals = params.value || []
        const indicators = ['Lazer', 'Trabalho', 'Deslocamento', 'Doméstico', 'Meta OMS']
        
        let html = `<div class="font-bold text-xs pb-1 mb-1.5 border-b border-stone-200 flex items-center gap-1.5">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background-color:${color};"></span>
          <span style="color:${color}">${escapeHtml(params.name)}</span>
        </div>`
        
        html += `<div class="space-y-1">`
        indicators.forEach((ind, idx) => {
          html += `
            <div class="flex items-center justify-between gap-4 text-xs">
              <span class="text-stone-600">${ind}</span>
              <span class="font-bold text-stone-900">${vals[idx] ? vals[idx].toFixed(1) + '%' : '—'}</span>
            </div>
          `
        })
        html += `</div>`
        return html
      }
    },
    radar: {
      indicator: [
        { name: 'Lazer & Esporte', max: radarMax },
        { name: 'Trabalho', max: radarMax },
        { name: 'Deslocamento', max: radarMax },
        { name: 'Doméstico', max: radarMax },
        { name: 'Meta OMS', max: radarMax }
      ],
      shape: 'polygon',
      splitNumber: 4,
      radius: '68%',
      center: ['50%', '52%'],
      axisName: {
        color: '#78716C',
        fontSize: 10.5,
        fontWeight: 600
      },
      splitLine: {
        lineStyle: {
          color: '#E7E5E4',
          type: 'dashed'
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(245, 245, 244, 0.5)', 'rgba(255, 255, 255, 0.8)']
        }
      },
      axisLine: {
        lineStyle: {
          color: '#E7E5E4'
        }
      }
    },
    series: [
      {
        name: 'Perfil de Atividade Física',
        type: 'radar',
        data: [
          {
            value: mascValues,
            name: 'Masculino',
            symbol: 'circle',
            symbolSize: 5,
            itemStyle: { color: '#3B82F6' },
            lineStyle: { width: 2.2, color: '#3B82F6' },
            areaStyle: { color: 'rgba(59, 130, 246, 0.22)' }
          },
          {
            value: femValues,
            name: 'Feminino',
            symbol: 'circle',
            symbolSize: 5,
            itemStyle: { color: '#EC4899' },
            lineStyle: { width: 2.2, color: '#EC4899' },
            areaStyle: { color: 'rgba(236, 72, 153, 0.22)' }
          }
        ]
      }
    ]
  }
})
</script>
