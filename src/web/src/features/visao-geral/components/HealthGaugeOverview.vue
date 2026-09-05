<template>
  <div
    class="bg-card border border-border rounded-xl shadow-xs overflow-hidden transition-all duration-300"
    role="region"
    aria-label="Índice de Saúde Populacional"
  >
    <!-- Header: Título, Badge de Nível (1 Palavra) e Popovers Explicativos -->
    <div class="px-4 py-2.5 border-b border-border/80 flex flex-wrap items-center justify-between gap-2 bg-surface/50">
      <div class="flex items-center gap-2">
        <div
          class="w-2.5 h-2.5 rounded-full ring-4 transition-all duration-300"
          :class="healthClassification.dotClass"
        ></div>
        <div>
          <h3 class="text-sm font-semibold text-text-primary tracking-tight font-display flex items-center gap-2">
            Índice de Saúde Populacional
            <span class="text-xs font-normal text-text-secondary font-sans hidden sm:inline">
              {{ breakdown?.isAdapted ? '(Síntese Adaptada dos 2 Eixos — Pré-2016)' : '(Síntese Ponderada dos 3 Eixos)' }}
            </span>
          </h3>
        </div>
      </div>

      <!-- Lado Direito: Badge de Classificação (1 Palavra) + Popover Metodológico GBD/PAF -->
      <div class="flex items-center gap-2">
        <!-- Badge de Classificação com Popover Explicativo do Nível -->
        <div
          v-if="!isLoading && healthClassification"
          class="relative group/status inline-flex items-center cursor-help"
          tabindex="0"
          :aria-label="`Nível de classificação: ${healthClassification.label}`"
        >
          <span
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border tracking-wide transition-colors duration-200"
            :class="healthClassification.badgeClass"
          >
            <span class="w-1.5 h-1.5 rounded-full mr-1.5" :style="{ backgroundColor: healthClassification.color }"></span>
            {{ healthClassification.label }}
          </span>

          <!-- Popover Explicativo Detalhado do Nível -->
          <div class="absolute right-0 top-full mt-2 w-76 p-3 bg-stone-900 text-stone-100 rounded-lg shadow-2xl border border-stone-700 text-xs opacity-0 invisible group-hover/status:opacity-100 group-focus/status:opacity-100 group-hover/status:visible group-focus/status:visible transition-all duration-200 z-50 pointer-events-none text-left">
            <div class="font-bold mb-1 text-[11px] uppercase tracking-wider font-display" :style="{ color: healthClassification.color }">
              Nível: {{ healthClassification.label }}
            </div>
            <p class="leading-relaxed text-stone-200 text-[11px] font-sans">
              {{ healthClassification.description }}
            </p>
            <div class="mt-2 pt-1.5 border-t border-stone-800 text-[10px] text-stone-400 flex items-center justify-between font-mono">
              <span>Faixas da Escala:</span>
              <span class="text-stone-300">&lt;50 Crítico | 50–69 Atenção | ≥70 Favorável</span>
            </div>
            <div class="w-2.5 h-2.5 bg-stone-900 border-t border-l border-stone-700 transform rotate-45 absolute -top-1.5 right-6"></div>
          </div>
        </div>

        <!-- Popover Informativo Metodológico Dark Stone -->
        <div class="relative group/method inline-flex items-center cursor-help">
          <button
            type="button"
            class="text-xs text-text-secondary hover:text-text-primary bg-stone-100 hover:bg-stone-200/80 border border-stone-200/80 px-2 py-0.5 rounded-md font-medium transition-colors flex items-center gap-1.5 focus:outline-hidden"
            aria-haspopup="dialog"
            aria-label="Metodologia e fórmula do índice"
          >
            <span class="text-[11px]">Como é calculado?</span>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5 text-stone-400 group-hover/method:text-stone-600 transition-colors" aria-hidden="true">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
            </svg>
          </button>

          <!-- Popover Dark Glass com Explicação Científica e Fórmula -->
          <div class="absolute right-0 top-full mt-2 w-88 p-3.5 bg-stone-900 text-stone-100 rounded-lg shadow-2xl border border-stone-700 text-xs opacity-0 invisible group-hover/method:opacity-100 group-focus-within/method:opacity-100 group-hover/method:visible group-focus-within/method:visible transition-all duration-200 z-50 pointer-events-none text-left">
            <div class="font-bold mb-1 text-[11px] uppercase tracking-wider text-teal font-display">
              Fórmula e Ponderação Epidemiológica
            </div>
            <p class="leading-relaxed text-stone-200 text-[11px] font-sans">
              O score é a <b>soma ponderada direta</b> dos eixos de vigilância VIGITEL, fundamentada na Fração Atribuível Populacional (PAF) do <b>GBD 2021 (IHME/Lancet)</b> para o Brasil:
            </p>
            <div class="my-2 p-2 rounded bg-stone-800 border border-stone-700 font-mono text-[10.5px] text-stone-200 space-y-1">
              <div class="text-[10px] text-teal-400 font-sans font-bold uppercase tracking-wider">Período 2016–2023 (3 Eixos):</div>
              <div><span class="text-teal font-bold">+ (Atividade Física × 0.30)</span> <span class="text-stone-400">→ protetor</span></div>
              <div><span class="text-amber font-bold">+ ((100 - Telas) × 0.20)</span> <span class="text-stone-400">→ risco invertido</span></div>
              <div><span class="text-red font-bold">+ ((100 - Obesidade) × 0.50)</span> <span class="text-stone-400">→ maior impacto</span></div>
            </div>
            <div class="my-2 p-2 rounded bg-stone-800/80 border border-stone-700 font-mono text-[10.5px] text-stone-200 space-y-1">
              <div class="text-[10px] text-amber-400 font-sans font-bold uppercase tracking-wider">Período Pré-2016 (Adaptado 2 Eixos):</div>
              <div class="text-[10px] text-stone-300 font-sans leading-tight">Como telas não eram coletadas no VIGITEL antes de 2016, aplica-se a renormalização proporcional:</div>
              <div><span class="text-teal font-bold">+ (Atividade Física × 0.375)</span> <span class="text-stone-400">(37,5%)</span></div>
              <div><span class="text-red font-bold">+ ((100 - Obesidade) × 0.625)</span> <span class="text-stone-400">(62,5%)</span></div>
            </div>
            <p class="text-[10px] text-stone-300 font-sans">
              * Fatores de risco são invertidos: quanto menor o sedentarismo e a obesidade, maior a pontuação de saúde gerada.
            </p>
            <div class="w-2.5 h-2.5 bg-stone-900 border-t border-l border-stone-700 transform rotate-45 absolute -top-1.5 right-4"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Conteúdo Principal com Layout Harmonizado e Compacto -->
    <div class="p-3 sm:p-4">
      <!-- Loading Skeleton -->
      <div v-if="isLoading" class="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-5 items-start">
        <div class="lg:col-span-5 flex flex-col items-center justify-center py-4 animate-pulse">
          <div class="w-48 h-24 bg-stone-200/80 rounded-t-full mb-3"></div>
          <div class="h-6 w-32 bg-stone-200/80 rounded mb-2"></div>
          <div class="h-3.5 w-44 bg-stone-200/80 rounded"></div>
        </div>
        <div class="lg:col-span-7 flex flex-col gap-2 sm:gap-2.5">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 xl:gap-3">
            <div v-for="i in 3" :key="i" class="h-28 bg-stone-100 animate-pulse rounded-xl border border-border/50"></div>
          </div>
          <div class="h-14 bg-stone-100 animate-pulse rounded-xl border border-border/50"></div>
        </div>
      </div>

      <!-- Dados Indisponíveis -->
      <div v-else-if="healthIndex === null" class="text-center py-8 text-text-muted">
        <svg class="w-10 h-10 mx-auto mb-2 text-text-muted/60" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-sm font-medium">Dados insuficientes para calcular o índice com os filtros selecionados.</p>
        <p class="text-xs text-text-muted mt-0.5">Experimente ampliar o intervalo de anos ou limpar os filtros demográficos.</p>
      </div>

      <!-- Termômetro e Grid de Cards com Barra de Composição Inferior -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-5 items-start">
        <!-- Coluna Esquerda: Gauge Chart ECharts + Legenda das 3 Faixas -->
        <div class="lg:col-span-5 flex flex-col items-center justify-center relative">
          <!-- Container do Termômetro com Altura Calibrada e Ótima Legibilidade -->
          <div class="relative w-full h-[210px] sm:h-[220px] min-h-[200px] flex items-center justify-center">
            <v-chart
              :option="gaugeOption"
              autoresize
              class="w-full h-full"
            />
          </div>

          <!-- Legenda das 3 Faixas do Termômetro -->
          <div class="flex items-center justify-center gap-3.5 text-[11px] font-mono text-text-secondary mt-1">
            <span class="flex items-center gap-1.5 font-medium">
              <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: HEALTH_INDEX_COLORS.CRITICAL }"></span> &lt;50 Crítico
            </span>
            <span class="flex items-center gap-1.5 font-medium">
              <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: HEALTH_INDEX_COLORS.ATTENTION }"></span> 50–69 Atenção
            </span>
            <span class="flex items-center gap-1.5 font-medium">
              <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: HEALTH_INDEX_COLORS.FAVORABLE }"></span> ≥70 Favorável
            </span>
          </div>
        </div>

        <!-- Coluna Direita: Cards Elevados + Barra de Composição da Soma na Base -->
        <div class="lg:col-span-7 flex flex-col gap-2 sm:gap-2.5">
          <!-- Topo: Os 3 Mini-Sparkline Cards Lado a Lado (Posicionados no Topo) -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 xl:gap-3">
            <!-- Card 1: Atividade Física -->
            <HealthSparkCard
              title="Atividade Física"
              category="Fator Protetor"
              :weight="breakdown?.atividade?.weight ?? 30"
              :points="breakdown?.atividade?.points"
              :maxPoints="breakdown?.atividade?.maxPoints"
              :formulaText="breakdown?.atividade?.formulaText"
              :value="visaoGeral?.atinge_150min?.value"
              :trend="visaoGeral?.atinge_150min?.trend"
              :invertedTrend="false"
              color="teal"
              colorHex="#0D9488"
              :evolutionData="evolucaoAtividadeFisica"
              dataKey="atinge_150min"
              tooltipTitle="Recomendação OMS (≥150 min/sem)"
              tooltipText="Adultos que cumprem as diretrizes da OMS somando lazer, deslocamento e ocupação. Principal pilar de proteção cardiometabólica."
              :isLoading="isLoading"
            />

            <!-- Card 2: Excesso de Telas -->
            <HealthSparkCard
              title="Excesso de Telas"
              category="Fator de Risco"
              :weight="breakdown?.sedentarismo?.weight ?? 20"
              :points="breakdown?.isAdapted ? null : breakdown?.sedentarismo?.points"
              :maxPoints="breakdown?.sedentarismo?.maxPoints"
              :formulaText="breakdown?.sedentarismo?.formulaText"
              :isAvailable="!breakdown?.isAdapted"
              unavailableNotice="Série iniciada em 2016"
              :value="visaoGeral?.tempo_tela_maior_3h?.value"
              :trend="visaoGeral?.tempo_tela_maior_3h?.trend"
              :invertedTrend="true"
              color="amber"
              colorHex="#D97706"
              :evolutionData="evolucaoSedentarismo"
              dataKey="tempo_tela_maior_3h"
              tooltipTitle="Comportamento Sedentário (≥3h)"
              tooltipText="Adultos com 3 horas ou mais de tempo livre em telas (TV, smartphone, computador). Fator de risco metabólico independente."
              :isLoading="isLoading"
            />

            <!-- Card 3: Obesidade -->
            <HealthSparkCard
              title="Obesidade"
              category="Fator de Risco"
              :weight="breakdown?.obesidade?.weight ?? 50"
              :points="breakdown?.obesidade?.points"
              :maxPoints="breakdown?.obesidade?.maxPoints"
              :formulaText="breakdown?.obesidade?.formulaText"
              :value="visaoGeral?.obesidade?.value"
              :trend="visaoGeral?.obesidade?.trend"
              :invertedTrend="true"
              color="red"
              colorHex="#DC2626"
              :evolutionData="evolucaoDesfechos"
              dataKey="obesidade"
              tooltipTitle="Desfecho Crônico (IMC ≥ 30)"
              tooltipText="Maior determinante atribuível a DCNTs no Brasil. Ponderado com o maior peso (50%) devido ao seu impacto maciço na carga de morbimortalidade."
              :isLoading="isLoading"
            />
          </div>

          <!-- Base: Barra de Composição Ponderada (Largura Total sob os 3 Cards) -->
          <div
            v-if="breakdown"
            class="p-2 sm:px-3 sm:py-2.5 bg-surface/80 hover:bg-surface border border-border/80 rounded-xl w-full shadow-2xs transition-colors"
          >
            <div class="flex items-center justify-between text-xs font-semibold text-text-primary mb-1">
              <span class="flex items-center gap-1.5">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-text-secondary" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.715-5.349L11 6.477V16h2a1 1 0 110 2H7a1 1 0 110-2h2V6.477L6.237 7.582l1.715 5.349a1 1 0 01-.285 1.05A3.989 3.989 0 015 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.788l1.599.799L9 4.323V3a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                <span class="text-text-secondary text-[11px] uppercase tracking-wider font-display font-bold">Composição da Soma</span>
                <span class="font-mono text-text-primary font-bold">({{ breakdown.total }} pts)</span>
              </span>
              <span class="text-[10px] text-text-muted font-mono bg-stone-100/90 px-1.5 py-0.5 rounded border border-stone-200/70">Meta Ideal: 80 pts</span>
            </div>

            <!-- Barra Segmentada Empilhada Proporcional aos Pontos Gerados -->
            <div class="w-full h-2 rounded-full overflow-hidden flex bg-stone-200/80 my-1.5 border border-stone-200/60 shadow-inner" title="Pontos somados para atingir a meta de 100 pts">
              <div
                class="bg-teal transition-all duration-500"
                :style="{ width: `${breakdown.atividade.points}%` }"
                :title="`Atividade Física: +${breakdown.atividade.points} pts`"
              ></div>
              <div
                v-if="!breakdown.isAdapted"
                class="bg-amber transition-all duration-500"
                :style="{ width: `${breakdown.sedentarismo.points}%` }"
                :title="`Excesso de Telas: +${breakdown.sedentarismo.points} pts`"
              ></div>
              <div
                class="bg-red transition-all duration-500"
                :style="{ width: `${breakdown.obesidade.points}%` }"
                :title="`Obesidade: +${breakdown.obesidade.points} pts`"
              ></div>
            </div>

            <!-- Equação Matemática Visual Reativa -->
            <div class="mt-1 flex items-center justify-between text-[11px] font-mono text-text-secondary flex-wrap gap-1">
              <div class="flex items-center gap-1.5 flex-wrap">
                <span class="inline-flex items-center gap-1 text-teal font-semibold" :title="breakdown.atividade.formulaText">
                  <span class="w-1.5 h-1.5 rounded-full bg-teal shrink-0"></span>
                  +{{ breakdown.atividade.points }} AF
                </span>
                <span class="text-stone-300 font-bold">+</span>
                <template v-if="!breakdown.isAdapted">
                  <span class="inline-flex items-center gap-1 text-amber font-semibold" :title="breakdown.sedentarismo.formulaText">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber shrink-0"></span>
                    +{{ breakdown.sedentarismo.points }} Telas
                  </span>
                  <span class="text-stone-300 font-bold">+</span>
                </template>
                <span class="inline-flex items-center gap-1 text-red font-semibold" :title="breakdown.obesidade.formulaText">
                  <span class="w-1.5 h-1.5 rounded-full bg-red shrink-0"></span>
                  +{{ breakdown.obesidade.points }} Obesidade
                </span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-stone-300 font-bold">=</span>
                <span class="font-bold text-text-primary bg-stone-100 px-2 py-0.5 rounded border border-stone-200/80 text-xs shadow-2xs">{{ breakdown.total }} pts</span>
              </div>
            </div>

            <!-- Aviso de Adaptação Pré-2016 -->
            <div v-if="breakdown.isAdapted" class="mt-1.5 pt-1.5 border-t border-border/60 flex items-start gap-1.5 text-[10px] text-amber-800">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5 shrink-0 text-amber-600 mt-0.5" aria-hidden="true">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
              </svg>
              <span><b>Período pré-2016</b>: pesos adaptados proporcionalmente (AF: 37,5%, Obesidade: 62,5%) pela ausência da série de telas no VIGITEL.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useIndicadores } from '../../core/composables/useIndicadores'
import {
  getHealthIndexBreakdown,
  classifyHealthIndex,
  HEALTH_INDEX_COLORS
} from '../utils/healthIndex'
import HealthSparkCard from './HealthSparkCard.vue'

const {
  visaoGeral,
  evolucaoAtividadeFisica,
  evolucaoSedentarismo,
  evolucaoDesfechos,
  isLoading
} = useIndicadores()

// Computa a decomposição epidemiológica (Single Source of Truth para o score)
const breakdown = computed(() => {
  return getHealthIndexBreakdown(
    visaoGeral.value?.atinge_150min?.value,
    visaoGeral.value?.tempo_tela_maior_3h?.value,
    visaoGeral.value?.obesidade?.value
  )
})

// Deriva o score diretamente do breakdown (eliminando re-cálculo redundante a cada filtro)
const healthIndex = computed(() => breakdown.value?.total ?? null)

// Classificação com labels de 1 palavra e tokens de design centralizados
const healthClassification = computed(() => {
  return classifyHealthIndex(healthIndex.value)
})

// Configuração ampliada, nítida e calibrada do Gauge ECharts
const gaugeOption = computed(() => {
  if (healthIndex.value === null) return {}

  const currentScore = healthIndex.value
  const classification = healthClassification.value

  return {
    series: [
      {
        type: 'gauge',
        startAngle: 200,
        endAngle: -20,
        min: 0,
        max: 100,
        radius: '96%',
        center: ['50%', '52%'],
        animationDuration: 1200,
        animationEasing: 'cubicOut',
        // Faixa com os 3 segmentos nítidos e espessos (14px) correspondendo exatamente à legenda
        axisLine: {
          lineStyle: {
            width: 14,
            color: [
              [0.5, HEALTH_INDEX_COLORS.CRITICAL],
              [0.7, HEALTH_INDEX_COLORS.ATTENTION],
              [1.0, HEALTH_INDEX_COLORS.FAVORABLE]
            ]
          }
        },
        progress: {
          show: false
        },
        // Agulha elegante, fina e com comprimento proporcional
        pointer: {
          show: true,
          length: '54%',
          width: 3.5,
          itemStyle: {
            color: '#1C1917'
          }
        },
        // Âncora (pivô) discreta e posicionada abaixo do texto (showAbove: false)
        anchor: {
          show: true,
          showAbove: false,
          size: 6,
          itemStyle: {
            color: '#1C1917'
          }
        },
        // Marcas menores
        axisTick: {
          show: true,
          splitNumber: 4,
          distance: 4,
          length: 4,
          lineStyle: {
            color: '#A8A29E',
            width: 1
          }
        },
        // Divisórias principais
        splitLine: {
          show: true,
          distance: 4,
          length: 8,
          lineStyle: {
            color: '#78716C',
            width: 2
          }
        },
        // Labels numéricos nas metas críticas (0, 50, 70, 100)
        axisLabel: {
          distance: 12,
          color: '#57534E',
          fontSize: 11,
          fontFamily: 'JetBrains Mono, monospace',
          formatter: (val) => {
            if (val === 0 || val === 50 || val === 70 || val === 100) {
              return `${val}`
            }
            return ''
          }
        },
        // Título central (Nível em 1 palavra única, posicionado confortavelmente abaixo do número)
        title: {
          show: true,
          offsetCenter: [0, '54%'],
          fontSize: 15,
          fontWeight: 700,
          color: classification.color,
          fontFamily: 'Plus Jakarta Sans, sans-serif'
        },
        // Valor central (Pontuação) com tipografia destacada e ampla legibilidade
        detail: {
          valueAnimation: true,
          formatter: (val) => {
            const num = Number(val)
            return isNaN(num) ? '' : num.toFixed(1)
          },
          offsetCenter: [0, '22%'],
          fontSize: 34,
          fontWeight: 800,
          fontFamily: 'JetBrains Mono, monospace',
          color: '#1C1917'
        },
        data: [
          {
            value: currentScore,
            name: classification.label
          }
        ]
      }
    ]
  }
})
</script>
