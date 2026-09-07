<template>
  <div class="bg-card border border-border rounded-xl shadow-sm p-3.5 sm:p-4 xl:p-5 flex flex-col justify-between h-full relative">
    
    <!-- Topo: Cabeçalho do Card com Popover Explicativo no Hover/Touch -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 sm:gap-2 pb-2.5 sm:pb-3 border-b border-border/60">
      <div class="flex items-center gap-2 min-w-0">
        <div class="w-2.5 h-2.5 rounded-full bg-amber shrink-0 shadow-xs"></div>
        <h3 class="text-xs sm:text-sm font-bold text-text-primary uppercase tracking-wide font-display truncate sm:overflow-visible">
          Evolução Histórica do Sedentarismo
        </h3>

        <!-- Botão Informativo com Popover Explicativo no Hover/Touch -->
        <div class="relative group/info shrink-0 cursor-help">
          <button
            type="button"
            @click.stop="toggleInfo"
            class="w-5 h-5 rounded-full bg-stone-100 hover:bg-stone-200/80 border border-stone-200 flex items-center justify-center text-text-secondary transition-colors shadow-2xs cursor-pointer active:scale-95"
            aria-label="Informações sobre Tempo Prolongado de Tela"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
            </svg>
          </button>

          <!-- Popover Informativo Flutuante -->
          <div
            @click.stop
            class="absolute left-0 top-full mt-2 w-72 max-w-[calc(100vw-32px)] p-3 bg-stone-900 text-stone-100 rounded-lg shadow-xl border border-stone-700 text-xs opacity-0 invisible group-hover/info:opacity-100 group-hover/info:visible transition-all duration-200 z-50 pointer-events-none"
            :class="{ '!opacity-100 !visible !pointer-events-auto': isInfoOpen }"
          >
            <div class="font-bold text-amber-400 mb-1 text-[11px] uppercase tracking-wider">
              Tempo Prolongado de Tela
            </div>
            <p class="leading-relaxed text-stone-200 text-[11px]">
              Acompanhamento histórico da proporção (%) de adultos expostos a tempo prolongado de tela (>3h/dia) no lazer, comparando Televisão e Dispositivos Digitais (computador, tablet e celular).
            </p>
            <div class="w-2.5 h-2.5 bg-stone-900 border-t border-l border-stone-700 transform rotate-45 absolute -top-1.5 left-2"></div>
          </div>
        </div>
      </div>

      <!-- Badge Informativo: Toque/Clique na legenda para isolar -->
      <div class="flex items-center gap-1.5 text-[10.5px] sm:text-xs text-amber font-medium bg-amber/10 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-md shrink-0 self-start sm:self-auto">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
        </svg>
        <span class="hidden sm:inline">Clique na legenda para isolar</span>
        <span class="sm:hidden">Toque na legenda para isolar</span>
      </div>
    </div>

    <!-- Centro: Gráfico ECharts -->
    <div class="relative w-full h-[290px] sm:h-[330px] xl:h-[370px] 2xl:h-[410px] mt-2">
      <!-- Loading Skeleton -->
      <div v-if="isLoading" class="absolute inset-0 z-10 bg-card">
        <ChartSkeleton type="line" />
      </div>

      <!-- Empty State -->
      <div v-else-if="!hasData" class="absolute inset-0 flex flex-col justify-center items-center gap-2 text-center p-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-stone-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <p class="text-sm font-semibold text-text-primary">Nenhum dado histórico encontrado</p>
        <p class="text-xs text-text-secondary">Tente ajustar os filtros globais para visualizar a série temporal.</p>
      </div>

      <!-- ECharts Component -->
      <v-chart
        v-else
        class="w-full h-full"
        :option="chartOption"
        autoresize
      />
    </div>

    <!-- Rodapé: Legenda / Nota explicativa com Tooltip Interativo -->
    <div class="mt-1 pt-2 border-t border-border/40 flex flex-wrap items-center justify-between gap-2 text-[11px] text-text-muted">
      <div class="flex items-center gap-2">
        <span>Fonte: Sistema VIGITEL / Ministério da Saúde</span>
        <span class="inline-block w-1 h-1 rounded-full bg-stone-300"></span>
        
        <!-- Badge de Atenção Metodológica com Popover no Hover/Touch -->
        <div class="relative group/metodo inline-flex items-center cursor-help">
          <button
            type="button"
            @click.stop="toggleMetodo"
            class="text-amber-800 font-semibold bg-amber-50 hover:bg-amber-100/90 active:scale-95 px-2 py-0.5 rounded-md border border-amber-200/70 transition-colors flex items-center gap-1 cursor-pointer"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5 text-amber-600">
              <path fill-rule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
            </svg>
            <span>2016: Introdução das telas digitais (celular/computador)</span>
          </button>

          <!-- Popover Informativo Detalhado (Hover/Touch) -->
          <div
            @click.stop
            class="absolute bottom-full left-0 mb-2 w-72 sm:w-80 lg:w-96 max-w-[calc(100vw-32px)] p-3.5 bg-stone-900 text-stone-100 rounded-lg shadow-xl border border-stone-700 text-xs opacity-0 invisible group-hover/metodo:opacity-100 group-hover/metodo:visible transition-all duration-200 z-50 pointer-events-none"
            :class="{ '!opacity-100 !visible !pointer-events-auto': isMetodoOpen }"
          >
            <div class="flex items-center gap-1.5 font-bold text-amber-400 mb-1.5 pb-1 border-b border-stone-700 text-[11px] uppercase tracking-wider">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
              </svg>
              <span>Nota Metodológica Oficial (VIGITEL / MS)</span>
            </div>
            <p class="leading-relaxed text-stone-200 text-[11px]">
              Entre <strong>2006 e 2015</strong>, o questionário VIGITEL mensurava o sedentarismo exclusivamente por meio do hábito de assistir à televisão (≥3h/dia). A partir de <strong>2016</strong>, em consonância com a disseminação de smartphones e tablets, foram introduzidas perguntas sobre o tempo despendido em computadores e outros dispositivos digitais no lazer, permitindo a consolidação do indicador composto de <strong>Tempo Total de Tela</strong>.
            </p>
            <div class="w-2.5 h-2.5 bg-stone-900 border-b border-r border-stone-700 transform rotate-45 absolute -bottom-1.5 left-6"></div>
          </div>
        </div>

      </div>
      <span>Arraste os seletores do eixo inferior para filtrar o intervalo de anos</span>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import ChartSkeleton from '../../core/components/ui/ChartSkeleton.vue'
import { escapeHtml } from '../../../utils/sanitize'
import { getAdaptivePrevalenceCeiling } from '../../../utils/chartScales'
import { useTouchTooltip } from '../../core/composables/useTouchTooltip'

const { isOpen: isInfoOpen, toggle: toggleInfo } = useTouchTooltip()
const { isOpen: isMetodoOpen, toggle: toggleMetodo } = useTouchTooltip()

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

// Verifica se existem pontos válidos
const hasData = computed(() => {
  return Array.isArray(props.data) && props.data.length > 0
})

// Constrói a configuração reativa do Apache ECharts
const chartOption = computed(() => {
  if (!hasData.value) return {}

  // Ordena os dados cronologicamente
  const sorted = [...props.data].sort((a, b) => a.ano - b.ano)
  const years = sorted.map(d => d.ano)

  const telaTotalData = sorted.map(d => d.tempo_tela_maior_3h ?? null)
  const tvData = sorted.map(d => d.tempo_tv_maior_3h ?? null)
  const telaExcetoTvData = sorted.map(d => d.tempo_tela_exceto_tv_maior_3h ?? null)

  const item2016 = sorted.find(d => Number(d.ano) === 2016)
  const val2016 = item2016?.tempo_tela_maior_3h ?? 65

  return {
    tooltip: {
      trigger: 'axis',
      confine: true,
      backgroundColor: 'rgba(255, 255, 255, 0.98)',
      borderColor: '#E2E8F0',
      borderWidth: 1,
      padding: [10, 14],
      textStyle: {
        color: '#1C1917',
        fontSize: 12
      },
      axisPointer: {
        type: 'cross',
        lineStyle: {
          color: '#D97706',
          width: 1,
          type: 'dashed'
        },
        crossStyle: {
          color: '#D97706'
        }
      },
      formatter: (params) => {
        if (!params || !params.length) return ''
        const ano = escapeHtml(params[0].name)
        let html = `<div class="font-bold text-xs text-stone-800 pb-1 mb-1.5 border-b border-stone-200 flex items-center justify-between">
          <span>Ano: ${ano}</span>
          ${ano == 2016 ? '<span class="text-[10px] text-amber-700 bg-amber-50 px-1 rounded border border-amber-200">Início Telas Digitais</span>' : ''}
        </div>`
        html += `<div class="space-y-1">`
        
        params.forEach(item => {
          const val = (item.value !== null && item.value !== undefined) 
            ? `${Number(item.value).toFixed(1)}%` 
            : '<span class="text-stone-400">Não coletado</span>'
            
          html += `
            <div class="flex items-center justify-between gap-4 text-xs">
              <div class="flex items-center gap-1.5">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background-color:${escapeHtml(item.color)};"></span>
                <span class="text-stone-600">${escapeHtml(item.seriesName)}</span>
              </div>
              <span class="font-bold text-stone-900">${val}</span>
            </div>
          `
        })
        
        if (ano == 2016) {
          html += `<div class="mt-2 pt-1.5 border-t border-stone-200 text-[10px] text-amber-800 leading-tight">
            ℹ️ A partir de 2016 foram incluídas perguntas sobre celular, tablet e computador no lazer.
          </div>`
        }
        
        html += `</div>`
        return html
      }
    },
    legend: {
      top: '0%',
      left: 'center',
      icon: 'circle',
      itemWidth: 8,
      itemHeight: 8,
      itemGap: 16,
      textStyle: {
        color: '#78716C',
        fontSize: 11,
        fontWeight: 500
      }
    },
    grid: {
      left: '2%',
      right: '4%',
      top: '12%',
      bottom: '16%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: years,
      axisLine: {
        lineStyle: { color: '#E7E5E4' }
      },
      axisTick: { show: false },
      axisLabel: {
        color: '#78716C',
        fontSize: 11,
        margin: 10
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: (val) => getAdaptivePrevalenceCeiling(val, 80),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        formatter: '{value}%',
        color: '#A8A29E',
        fontSize: 10
      },
      splitLine: {
        lineStyle: {
          color: '#F5F5F4',
          type: 'dashed'
        }
      }
    },
    dataZoom: [
      {
        type: 'slider',
        left: 28,
        right: 36,
        bottom: '0%',
        height: 22,
        borderColor: '#E2E8F0',
        borderRadius: 6,
        backgroundColor: '#F8FAFC',
        fillerColor: 'rgba(217, 119, 6, 0.16)',
        handleSize: '110%',
        handleStyle: {
          color: '#D97706',
          borderColor: '#B45309',
          borderWidth: 1.5,
          shadowBlur: 3,
          shadowColor: 'rgba(0, 0, 0, 0.15)'
        },
        textStyle: {
          color: '#B45309',
          fontSize: 10,
          fontWeight: 'bold'
        },
        showDetail: true,
        dataBackground: {
          lineStyle: { color: '#CBD5E1', width: 1 },
          areaStyle: { color: '#E2E8F0' }
        },
        selectedDataBackground: {
          lineStyle: { color: '#D97706', width: 1.5 },
          areaStyle: { color: 'rgba(217, 119, 6, 0.25)' }
        }
      },
      {
        type: 'inside'
      }
    ],
    series: [
      {
        name: 'Tempo de Tela Total',
        type: 'line',
        smooth: true,
        connectNulls: false,
        showSymbol: false,
        symbolSize: 6,
        data: telaTotalData,
        itemStyle: { color: '#D97706' },
        lineStyle: { width: 3, color: '#D97706' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(217, 119, 6, 0.20)' },
              { offset: 1, color: 'rgba(217, 119, 6, 0.0)' }
            ]
          }
        },
        markPoint: {
          symbol: 'roundRect',
          symbolSize: [26, 22],
          itemStyle: {
            color: '#FEF3C7',
            borderColor: '#FDE68A',
            borderWidth: 1,
            shadowColor: 'rgba(0, 0, 0, 0.08)',
            shadowBlur: 3
          },
          label: {
            show: true,
            formatter: '⚠️',
            fontSize: 12,
            position: 'inside'
          },
          tooltip: {
            formatter: '2016: Introdução das Telas Digitais (Celular, Tablet e Computador)'
          },
          data: [
            {
              name: 'Início Telas Digitais',
              coord: ['2016', val2016],
              symbolOffset: [-17, 0]
            }
          ]
        },
        markLine: {
          symbol: ['none', 'none'],
          silent: true,
          label: {
            show: false
          },
          lineStyle: {
            color: '#D97706',
            type: 'dashed',
            width: 1.5
          },
          data: [
            { xAxis: '2016' }
          ]
        }
      },
      {
        name: 'Televisão',
        type: 'line',
        smooth: true,
        connectNulls: false,
        showSymbol: false,
        symbolSize: 6,
        data: tvData,
        itemStyle: { color: '#7C3AED' },
        lineStyle: { width: 2.2, color: '#7C3AED' }
      },
      {
        name: 'Telas Digitais exceto TV',
        type: 'line',
        smooth: true,
        connectNulls: false,
        showSymbol: false,
        symbolSize: 6,
        data: telaExcetoTvData,
        itemStyle: { color: '#0284C7' },
        lineStyle: { width: 2.2, color: '#0284C7', type: 'dashed' }
      }
    ]
  }
})
</script>
