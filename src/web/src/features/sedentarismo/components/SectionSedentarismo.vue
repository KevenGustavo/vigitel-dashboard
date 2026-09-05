<template>
  <div class="space-y-4">
    
    <!-- Banner de Alerta e Contexto Clínico (Design Premium em 1 Linha) -->
    <div class="flex items-center justify-between gap-4 px-4 py-2.5 rounded-lg bg-amber/5 border border-amber/20 text-xs text-text-secondary">
      <div class="flex items-center gap-3 min-w-0">
        <!-- Badge Profissional -->
        <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber text-white text-[11px] font-bold tracking-wide shrink-0 shadow-sm">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="w-3.5 h-3.5">
            <rect width="20" height="14" x="2" y="3" rx="2"/>
            <line x1="8" x2="16" y1="21" y2="21"/>
            <line x1="12" x2="12" y1="17" y2="21"/>
          </svg>
          <span>Risco Cardiometabólico</span>
        </div>

        <p class="truncate text-text-secondary">
          A permanência sedentária em telas por <strong>mais de 3 horas diárias</strong> no lazer atua como agravo independente para obesidade, hipertensão e diabetes tipo 2.
        </p>
      </div>
    </div>

    <!-- Mini KPI Cards Declarativos de Comportamento Sedentário -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <VariableCard
        v-for="(item, index) in SEDENTARISMO_ITEMS"
        :key="item.key"
        :label="item.label"
        :value="sedentarismo?.[item.key]"
        :subtitle="item.subtitle"
        :dotClass="item.dotClass"
        :titleColor="item.titleColor"
        :tooltipTitle="item.tooltipTitle"
        :tooltipText="item.tooltipText"
        :align="index === 2 ? 'right' : (index === 1 ? 'responsive' : 'left')"
        :isLoading="isLoading"
      />
    </div>

    <!-- Grid de Gráficos -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Coluna 1 & 2: Gráfico de Evolução Temporal (ECharts) -->
      <div class="lg:col-span-2">
        <SedentarismoEvolutionChart
          :data="evolucaoSedentarismo"
          :isLoading="isLoading"
        />
      </div>

      <!-- Coluna 3: Tempo de Tela por Faixa Etária (Barras Agrupadas) -->
      <div class="lg:col-span-1">
        <SedentarismoAgeBarChart
          :data="sedentarismoFaixaEtaria"
          :isLoading="isLoading"
        />
      </div>

    </div>

  </div>
</template>

<script setup>
import { useIndicadores } from '../../core/composables/useIndicadores'
import VariableCard from '../../core/components/cards/VariableCard.vue'
import SedentarismoEvolutionChart from './SedentarismoEvolutionChart.vue'
import SedentarismoAgeBarChart from './SedentarismoAgeBarChart.vue'

const SEDENTARISMO_ITEMS = [
  {
    key: 'tempo_tela_maior_3h',
    label: 'Tempo de Tela Total',
    dotClass: 'bg-amber-600',
    titleColor: 'text-amber-400',
    subtitle: 'TV + dispositivos digitais',
    tooltipTitle: 'Tempo Prolongado de Tela no Lazer',
    tooltipText: 'Proporção de adultos que despendem 3 horas ou mais do seu tempo livre diário diante de qualquer tipo de tela (TV, celular, tablet ou computador). Fator de risco cardiometabólico independente.'
  },
  {
    key: 'tempo_tv_maior_3h',
    label: 'Televisão Diária',
    dotClass: 'bg-purple-600',
    titleColor: 'text-purple-400',
    subtitle: 'Hábito passivo de TV',
    tooltipTitle: 'Tempo de Televisão no Lazer',
    tooltipText: 'Proporção de adultos com 3 horas ou mais diárias dedicadas exclusivamente à televisão no tempo livre. Monitorada ininterruptamente pelo VIGITEL desde 2006.'
  },
  {
    key: 'tempo_tela_exceto_tv_maior_3h',
    label: 'Telas Digitais exceto TV',
    dotClass: 'bg-sky-600',
    titleColor: 'text-sky-400',
    subtitle: 'Celular, tablet e computador',
    tooltipTitle: 'Telas Digitais no Tempo Livre',
    tooltipText: 'Proporção de adultos que utilizam computadores, tablets ou celulares por 3 horas ou mais do tempo livre diário para fins recreativos (redes sociais, jogos e vídeos). Monitorada a partir de 2016.'
  }
]

const {
  sedentarismo,
  sedentarismoFaixaEtaria,
  evolucaoSedentarismo,
  isLoading
} = useIndicadores()
</script>
