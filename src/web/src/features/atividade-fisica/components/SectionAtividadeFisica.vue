<template>
  <div class="space-y-4">
    
    <!-- Banner de Diretrizes OMS Otimizado (Design Premium em 1 Linha) -->
    <div class="flex items-center justify-between gap-4 px-4 py-2.5 rounded-lg bg-teal/5 border border-teal/20 text-xs text-text-secondary">
      <div class="flex items-center gap-3 min-w-0">
        <!-- Badge Profissional OMS -->
        <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-teal text-white text-[11px] font-bold tracking-wide shrink-0 shadow-sm">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="w-3.5 h-3.5">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
          <span>Diretrizes OMS</span>
        </div>

        <p class="truncate text-text-secondary">
          Meta populacional de pelo menos <strong>150 min/semana</strong> de atividade física moderada (ou 75 min vigorosa), mensurada nos 4 domínios da rotina.
        </p>
      </div>
    </div>

    <!-- Mini KPI Cards Declarativos por Domínio de Atividade Física -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 xl:gap-3">
      <VariableCard
        v-for="(item, index) in ATIVIDADE_ITEMS"
        :key="item.key"
        :label="item.label"
        :value="atividadeFisica?.[item.key]"
        :subtitle="item.subtitle"
        :dotClass="item.dotClass"
        :titleColor="item.titleColor"
        :tooltipTitle="item.tooltipTitle"
        :tooltipText="item.tooltipText"
        :align="index >= 3 ? 'right' : (index === 1 ? 'responsive' : 'left')"
        :isLoading="isLoading"
      />
    </div>

    <!-- Grid de Gráficos -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-3.5 sm:gap-4 xl:gap-5">
      
      <!-- Coluna 1 & 2: Gráfico de Evolução Temporal (ECharts) -->
      <div class="lg:col-span-2">
        <AtividadeEvolutionChart
          :data="evolucaoAtividadeFisica"
          :isLoading="isLoading"
        />
      </div>

      <!-- Coluna 3: Perfil por Sexo Biológico (Radar Chart) -->
      <div class="lg:col-span-1">
        <AtividadeSexRadarChart
          :data="comparativoSexo"
          :isLoading="isLoading"
        />
      </div>

    </div>

  </div>
</template>

<script setup>
import { useIndicadores } from '../../core/composables/useIndicadores'
import VariableCard from '../../core/components/cards/VariableCard.vue'
import AtividadeEvolutionChart from './AtividadeEvolutionChart.vue'
import AtividadeSexRadarChart from './AtividadeSexRadarChart.vue'

const ATIVIDADE_ITEMS = [
  {
    key: 'atinge_150min',
    label: 'Meta OMS',
    dotClass: 'bg-emerald-600',
    titleColor: 'text-emerald-400',
    subtitle: 'Recomendação global',
    tooltipTitle: 'Meta de Atividade Física OMS',
    tooltipText: 'Proporção de adultos que atingem a recomendação da OMS de pelo menos 150 min/semana de atividade física moderada (ou 75 min vigorosa), somando todos os 4 domínios da rotina diária.'
  },
  {
    key: 'ativo_lazer',
    label: 'Lazer Ativo',
    dotClass: 'bg-teal-600',
    titleColor: 'text-teal-400',
    subtitle: 'Tempo livre voluntário',
    tooltipTitle: 'Atividade Física no Lazer',
    tooltipText: 'Proporção de adultos que praticam esportes, exercícios físicos ou caminhadas no tempo livre com duração de pelo menos 150 min/semana moderada (ou 75 min vigorosa). Principal marcador de estilo de vida ativo voluntário.'
  },
  {
    key: 'ativo_deslocamento',
    label: 'Deslocamento',
    dotClass: 'bg-cyan-600',
    titleColor: 'text-cyan-400',
    subtitle: 'A pé ou bicicleta',
    tooltipTitle: 'Atividade Física no Deslocamento',
    tooltipText: 'Proporção de adultos que realizam trajetos a pé ou em bicicleta no percurso de ida e volta para trabalho ou estudo com duração cumulativa de pelo menos 30 minutos diários (ou 150 min/semana).'
  },
  {
    key: 'ativo_ocupacional',
    label: 'Trabalho',
    dotClass: 'bg-indigo-600',
    titleColor: 'text-indigo-400',
    subtitle: 'Caminhada ou esforço laboral',
    tooltipTitle: 'Atividade Física Ocupacional',
    tooltipText: 'Proporção de trabalhadores que andam bastante a pé ou carregam pesos e volumes habitualmente durante a sua jornada regular de trabalho.'
  },
  {
    key: 'ativo_domestico',
    label: 'Doméstico',
    dotClass: 'bg-rose-600',
    titleColor: 'text-rose-400',
    subtitle: 'Limpeza pesada no domicílio',
    tooltipTitle: 'Atividade Física no Ambiente Doméstico',
    tooltipText: 'Proporção de adultos responsáveis pela realização de faxina ou limpeza pesada no domicílio por pelo menos 3 a 4 dias por semana.'
  },
  {
    key: 'inativo_total',
    label: 'Inatividade Total',
    dotClass: 'bg-slate-500',
    titleColor: 'text-slate-400',
    subtitle: 'Insuficiente em todos',
    tooltipTitle: 'Inatividade Física Global',
    tooltipText: 'Proporção da população que não atinge nenhum dos critérios mínimos de atividade física em qualquer um dos 4 domínios da rotina diária.'
  }
]

const {
  atividadeFisica,
  comparativoSexo,
  evolucaoAtividadeFisica,
  isLoading
} = useIndicadores()
</script>
