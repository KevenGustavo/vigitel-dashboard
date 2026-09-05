<template>
  <div class="bg-card border border-border rounded-xl shadow-sm p-5 flex flex-col justify-between h-full relative">
    
    <!-- Topo: Cabeçalho do Card com Popover Explicativo no Hover -->
    <div class="flex items-center justify-between pb-3 border-b border-border/60">
      <div class="flex items-center gap-2">
        <div class="w-2.5 h-2.5 rounded-full bg-red shrink-0 shadow-xs"></div>
        <h3 class="text-sm font-bold text-text-primary uppercase tracking-wide font-display">
          Evolução Temporal de Agravos Crônicos
        </h3>

        <!-- Botão Informativo com Popover Explicativo no Hover -->
        <div class="relative group/info shrink-0 cursor-help">
          <div class="w-5 h-5 rounded-full bg-stone-100 hover:bg-stone-200/80 border border-stone-200 flex items-center justify-center text-text-secondary transition-colors shadow-2xs">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3 h-3">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
            </svg>
          </div>

          <!-- Popover Informativo Flutuante -->
          <div class="absolute left-0 top-full mt-2 w-72 p-3 bg-stone-900 text-stone-100 rounded-lg shadow-xl border border-stone-700 text-xs opacity-0 invisible group-hover/info:opacity-100 group-hover/info:visible transition-all duration-200 z-50 pointer-events-none">
            <div class="font-bold text-rose-400 mb-1 text-[11px] uppercase tracking-wider">
              Doenças Crônicas e Nutrição
            </div>
            <p class="leading-relaxed text-stone-200 text-[11px]">
              Série histórica de Doenças Crônicas Não Transmissíveis (Hipertensão, Diabetes, Depressão) e Estado Nutricional (Obesidade e Excesso de Peso) segundo critérios OMS/MS.
            </p>
            <div class="w-2.5 h-2.5 bg-stone-900 border-t border-l border-stone-700 transform rotate-45 absolute -top-1.5 left-2"></div>
          </div>
        </div>
      </div>

      <!-- Badge Informativo -->
      <div class="flex items-center gap-1.5 text-xs text-rose-600 font-medium bg-rose-50 px-2.5 py-1 rounded-md shrink-0 border border-rose-200/60">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
        </svg>
        <span>Clique na legenda para isolar</span>
      </div>
    </div>

    <!-- Centro: Gráfico ECharts -->
    <div class="relative w-full h-[380px] mt-2">
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
        <p class="text-xs text-text-secondary">Tente ajustar os filtros globais.</p>
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
        
        <!-- Badge de Atenção Metodológica com Popover no Hover -->
        <div class="relative group/metodo inline-flex items-center cursor-help">
          <span class="text-rose-800 font-semibold bg-rose-50 hover:bg-rose-100/90 px-2 py-0.5 rounded-md border border-rose-200/70 transition-colors flex items-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5 text-rose-600">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
            </svg>
            <span>Periodicidade das variáveis crônicas</span>
          </span>

          <!-- Popover Informativo Detalhado (Hover) -->
          <div class="absolute bottom-full left-0 mb-2 w-80 sm:w-96 p-3.5 bg-stone-900 text-stone-100 rounded-lg shadow-xl border border-stone-700 text-xs opacity-0 invisible group-hover/metodo:opacity-100 group-hover/metodo:visible transition-all duration-200 z-50 pointer-events-none">
            <div class="flex items-center gap-1.5 font-bold text-rose-400 mb-1.5 pb-1 border-b border-stone-700 text-[11px] uppercase tracking-wider">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
              </svg>
              <span>Nota sobre Cobertura Histórica</span>
            </div>
            <p class="leading-relaxed text-stone-200 text-[11px]">
              O Índice de Massa Corporal (<strong>Obesidade</strong> e <strong>Excesso de Peso</strong>) possui mensuração ininterrupta anual desde 2006. O rastreamento de <strong>Depressão</strong> foi incorporado com regularidade a partir de 2020. <strong>Hipertensão</strong> e <strong>Diabetes</strong> contam com módulos especializados em edições selecionadas do VIGITEL.
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

const hasData = computed(() => {
  return Array.isArray(props.data) && props.data.length > 0
})

const chartOption = computed(() => {
  if (!hasData.value) return {}

  const sorted = [...props.data].sort((a, b) => a.ano - b.ano)
  const years = sorted.map(d => d.ano)

  const excessoPesoData = sorted.map(d => d.excesso_peso ?? null)
  const obesidadeData = sorted.map(d => d.obesidade ?? null)
  const depressaoData = sorted.map(d => d.depressao ?? null)
  const hipertensaoData = sorted.map(d => d.hipertensao ?? null)
  const diabetesData = sorted.map(d => d.diabetes ?? null)

  return {
    tooltip: {
      trigger: 'axis',
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
          color: '#E11D48',
          width: 1,
          type: 'dashed'
        },
        crossStyle: {
          color: '#E11D48'
        }
      },
      formatter: (params) => {
        if (!params || !params.length) return ''
        const ano = escapeHtml(params[0].name)
        let html = `<div class="font-bold text-xs text-stone-800 pb-1 mb-1.5 border-b border-stone-200">
          <span>Ano: ${ano}</span>
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
      max: 70,
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
        fillerColor: 'rgba(225, 29, 72, 0.14)',
        handleSize: '110%',
        handleStyle: {
          color: '#E11D48',
          borderColor: '#BE123C',
          borderWidth: 1.5,
          shadowBlur: 3,
          shadowColor: 'rgba(0, 0, 0, 0.15)'
        },
        textStyle: {
          color: '#BE123C',
          fontSize: 10,
          fontWeight: 'bold'
        },
        showDetail: true,
        dataBackground: {
          lineStyle: { color: '#CBD5E1', width: 1 },
          areaStyle: { color: '#E2E8F0' }
        },
        selectedDataBackground: {
          lineStyle: { color: '#E11D48', width: 1.5 },
          areaStyle: { color: 'rgba(225, 29, 72, 0.25)' }
        }
      },
      {
        type: 'inside'
      }
    ],
    series: [
      {
        name: 'Excesso de Peso',
        type: 'line',
        smooth: true,
        connectNulls: false,
        showSymbol: false,
        symbolSize: 6,
        data: excessoPesoData,
        itemStyle: { color: '#F59E0B' },
        lineStyle: { width: 2.5, color: '#F59E0B' }
      },
      {
        name: 'Obesidade',
        type: 'line',
        smooth: true,
        connectNulls: false,
        showSymbol: false,
        symbolSize: 6,
        data: obesidadeData,
        itemStyle: { color: '#DC2626' },
        lineStyle: { width: 3, color: '#DC2626' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(220, 38, 38, 0.15)' },
              { offset: 1, color: 'rgba(220, 38, 38, 0.0)' }
            ]
          }
        }
      },
      {
        name: 'Depressão',
        type: 'line',
        smooth: true,
        connectNulls: false,
        showSymbol: true,
        symbolSize: 5,
        data: depressaoData,
        itemStyle: { color: '#0284C7' },
        lineStyle: { width: 2.2, color: '#0284C7', type: 'dashed' }
      },
      {
        name: 'Hipertensão',
        type: 'line',
        showSymbol: true,
        symbol: 'diamond',
        symbolSize: 8,
        data: hipertensaoData,
        itemStyle: { color: '#0D9488' },
        lineStyle: { width: 2.2, color: '#0D9488', type: 'dotted' }
      },
      {
        name: 'Diabetes',
        type: 'line',
        showSymbol: true,
        symbol: 'triangle',
        symbolSize: 8,
        data: diabetesData,
        itemStyle: { color: '#7C3AED' },
        lineStyle: { width: 2, color: '#7C3AED', type: 'dotted' }
      }
    ]
  }
})
</script>
