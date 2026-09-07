<template>
  <div class="space-y-4">
    
    <!-- Banner Clínico de 1 Linha -->
    <div class="flex items-center justify-between gap-4 px-4 py-2.5 rounded-lg bg-rose-500/5 border border-rose-500/20 text-xs text-text-secondary">
      <div class="flex items-center gap-3 min-w-0">
        <!-- Badge Profissional -->
        <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-rose-600 text-white text-[11px] font-bold tracking-wide shrink-0 shadow-sm">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="w-3.5 h-3.5">
            <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
          </svg>
          <span>Vigilância de DCNT</span>
        </div>

        <p class="truncate text-text-secondary">
          A inatividade física e o sedentarismo atuam como causas diretas para a escalada do <strong>excesso de peso</strong> e agravos metabólicos na população urbana.
        </p>
      </div>
    </div>

    <!-- Mini KPI Cards Declarativos de Prevalência de Desfechos de Saúde -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 xl:gap-3">
      <VariableCard
        v-for="(item, index) in DESFECHOS_ITEMS"
        :key="item.key"
        :label="item.label"
        :value="desfechos?.[item.key]"
        :subtitle="item.subtitle"
        :dotClass="item.dotClass"
        :titleColor="item.titleColor"
        :tooltipTitle="item.tooltipTitle"
        :tooltipText="item.tooltipText"
        :align="index >= 3 ? 'right' : (index === 2 ? 'responsive' : 'left')"
        :extraClass="item.extraClass"
        :isLoading="isLoading"
      />
    </div>

    <!-- Grid de Gráficos -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-3.5 sm:gap-4 xl:gap-5">
      <!-- Coluna 1 & 2: Gráfico de Evolução Temporal (ECharts) -->
      <div class="lg:col-span-2">
        <DesfechosEvolutionChart
          :data="evolucaoDesfechos"
          :isLoading="isLoading"
        />
      </div>

      <!-- Coluna 3: Ranking das 27 Capitais -->
      <div class="lg:col-span-1">
        <DesfechosCityRankingChart
          :data="rankingCidades"
          :currentIndicador="indicadorRanking"
          :isLoading="isLoading"
          @change-indicador="fetchRankingCidades"
        />
      </div>
    </div>

  </div>
</template>

<script setup>
import { useIndicadores } from '../../core/composables/useIndicadores'
import VariableCard from '../../core/components/cards/VariableCard.vue'
import DesfechosEvolutionChart from './DesfechosEvolutionChart.vue'
import DesfechosCityRankingChart from './DesfechosCityRankingChart.vue'

const DESFECHOS_ITEMS = [
  {
    key: 'obesidade',
    label: 'Obesidade',
    dotClass: 'bg-red-600',
    titleColor: 'text-rose-400',
    subtitle: 'Prevalência diagnóstica',
    tooltipTitle: 'Obesidade',
    tooltipText: 'Proporção de adultos com Índice de Massa Corporal (IMC) igual ou superior a 30 kg/m², calculada a partir de peso e altura autorreferidos na entrevista telefônica.'
  },
  {
    key: 'excesso_peso',
    label: 'Excesso de Peso',
    dotClass: 'bg-amber-500',
    titleColor: 'text-amber-400',
    subtitle: 'Sobrepeso + obesidade',
    tooltipTitle: 'Excesso de Peso',
    tooltipText: 'Proporção de adultos com Índice de Massa Corporal (IMC) igual ou superior a 25 kg/m², englobando tanto sobrepeso quanto obesidade clínica.'
  },
  {
    key: 'hipertensao',
    label: 'Hipertensão Arterial',
    dotClass: 'bg-teal-600',
    titleColor: 'text-teal-400',
    subtitle: 'Diagnóstico médico',
    tooltipTitle: 'Hipertensão Arterial',
    tooltipText: 'Proporção de adultos que relatam diagnóstico médico prévio de hipertensão arterial sistêmica ou que utilizam medicamentos anti-hipertensivos contínuos prescritos.'
  },
  {
    key: 'diabetes',
    label: 'Diabetes Mellitus',
    dotClass: 'bg-purple-600',
    titleColor: 'text-purple-400',
    subtitle: 'Glicemia alterada referida',
    tooltipTitle: 'Diabetes Mellitus',
    tooltipText: 'Proporção de adultos que relatam diagnóstico médico prévio de diabetes mellitus ou tratamento contínuo com hipoglicemiantes orais ou insulina.'
  },
  {
    key: 'depressao',
    label: 'Depressão Referida',
    dotClass: 'bg-sky-600',
    titleColor: 'text-sky-400',
    subtitle: 'Diagnóstico médico referido',
    extraClass: 'col-span-2 sm:col-span-1',
    tooltipTitle: 'Depressão Referida',
    tooltipText: 'Proporção de adultos que relatam diagnóstico médico prévio de depressão ou acompanhamento profissional por transtorno depressivo.'
  }
]

const {
  desfechos,
  evolucaoDesfechos,
  rankingCidades,
  indicadorRanking,
  fetchRankingCidades,
  isLoading
} = useIndicadores()
</script>
