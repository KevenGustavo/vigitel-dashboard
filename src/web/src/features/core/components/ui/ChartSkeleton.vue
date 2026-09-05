<template>
  <div class="w-full h-full flex flex-col justify-between p-2 select-none animate-pulse">
    
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- ESQUELETO 1: LINHAS / SÉRIE TEMPORAL                                 -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div v-if="type === 'line'" class="w-full h-full flex flex-col justify-between">
      <!-- Mini Legenda simulada no topo -->
      <div class="flex items-center gap-4 pb-2 border-b border-stone-100">
        <div class="flex items-center gap-1.5">
          <div class="w-2.5 h-2.5 rounded-full bg-stone-200"></div>
          <div class="h-2.5 w-16 bg-stone-200 rounded"></div>
        </div>
        <div class="flex items-center gap-1.5">
          <div class="w-2.5 h-2.5 rounded-full bg-stone-200"></div>
          <div class="h-2.5 w-20 bg-stone-200 rounded"></div>
        </div>
        <div class="flex items-center gap-1.5">
          <div class="w-2.5 h-2.5 rounded-full bg-stone-200"></div>
          <div class="h-2.5 w-14 bg-stone-200 rounded"></div>
        </div>
      </div>

      <!-- Área de Gráfico com Grid e Curvas -->
      <div class="relative flex-1 my-3 flex items-center">
        <!-- Grade horizontal pontilhada de apoio -->
        <div class="absolute inset-0 flex flex-col justify-between py-2 pointer-events-none">
          <div class="w-full border-b border-dashed border-stone-200/80"></div>
          <div class="w-full border-b border-dashed border-stone-200/80"></div>
          <div class="w-full border-b border-dashed border-stone-200/80"></div>
          <div class="w-full border-b border-stone-200"></div>
        </div>

        <!-- Curvas de Onda SVG Simulando Séries -->
        <svg class="w-full h-44 text-stone-200" viewBox="0 0 500 150" fill="none" preserveAspectRatio="none">
          <!-- Linha 1 -->
          <path
            d="M 10 110 Q 90 80, 160 95 T 320 60 T 490 40"
            stroke="currentColor"
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="opacity-60"
          />
          <!-- Linha 2 -->
          <path
            d="M 10 135 Q 120 120, 220 100 T 360 85 T 490 70"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="opacity-40"
          />
          <!-- Linha 3 -->
          <path
            d="M 10 60 Q 140 75, 250 55 T 390 45 T 490 30"
            stroke="currentColor"
            stroke-width="2"
            stroke-dasharray="4 4"
            class="opacity-35"
          />
        </svg>
      </div>

      <!-- Ticks do Eixo X (Anos) -->
      <div class="flex justify-between items-center pt-1 border-t border-stone-200/60 text-[10px]">
        <div class="h-2 w-7 bg-stone-200 rounded"></div>
        <div class="h-2 w-7 bg-stone-200 rounded"></div>
        <div class="h-2 w-7 bg-stone-200 rounded"></div>
        <div class="h-2 w-7 bg-stone-200 rounded"></div>
        <div class="h-2 w-7 bg-stone-200 rounded"></div>
        <div class="h-2 w-7 bg-stone-200 rounded"></div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- ESQUELETO 2: RADAR                                                   -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div v-else-if="type === 'radar'" class="w-full h-full flex flex-col items-center justify-center relative py-2">
      <!-- Rótulo Superior -->
      <div class="h-2.5 w-16 bg-stone-200 rounded mb-2"></div>

      <!-- Teia do Radar com Anéis Concêntricos e Eixos -->
      <div class="relative w-48 h-48 flex items-center justify-center">
        <!-- Anel Externo -->
        <div class="absolute inset-0 rounded-full border border-dashed border-stone-300"></div>
        <!-- Anel Intermediário -->
        <div class="absolute inset-6 rounded-full border border-dashed border-stone-200"></div>
        <!-- Anel Interno -->
        <div class="absolute inset-14 rounded-full border border-stone-200/80"></div>
        
        <!-- Eixos Radiais Cruzados -->
        <div class="absolute w-full h-[1px] bg-stone-200"></div>
        <div class="absolute h-full w-[1px] bg-stone-200"></div>
        <div class="absolute w-full h-[1px] bg-stone-200 transform rotate-45"></div>
        <div class="absolute w-full h-[1px] bg-stone-200 transform -rotate-45"></div>

        <!-- Forma de Polígono Interno translúcido -->
        <div class="w-24 h-24 bg-stone-200/50 rounded-2xl rotate-12 transform border border-stone-300/80"></div>
      </div>

      <!-- Rótulos Laterais e Inferiores -->
      <div class="w-full flex justify-between px-4 mt-2">
        <div class="h-2.5 w-14 bg-stone-200 rounded"></div>
        <div class="h-2.5 w-14 bg-stone-200 rounded"></div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <!-- ESQUELETO 3: BARRAS HORIZONTAIS AGRUPADAS                            -->
    <!-- ══════════════════════════════════════════════════════════════════════ -->
    <div v-else-if="type === 'bar'" class="w-full h-full flex flex-col justify-between py-1">
      <div v-for="i in 6" :key="i" class="space-y-1.5">
        <!-- Label da Categoria (Faixa Etária) -->
        <div class="flex items-center justify-between">
          <div class="h-2.5 w-12 bg-stone-200 rounded"></div>
          <div class="h-2 w-8 bg-stone-200 rounded"></div>
        </div>

        <!-- Par de Barras Horizontais (Digital vs TV) -->
        <div class="space-y-1">
          <div
            class="h-2 bg-stone-200 rounded-full"
            :style="{ width: `${85 - (i * 9)}%` }"
          ></div>
          <div
            class="h-1.5 bg-stone-100 rounded-full"
            :style="{ width: `${35 + (i * 7)}%` }"
          ></div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'line',
    validator: (v) => ['line', 'radar', 'bar'].includes(v)
  }
})
</script>
