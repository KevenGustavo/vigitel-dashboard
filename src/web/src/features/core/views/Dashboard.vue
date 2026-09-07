<template>
  <div class="space-y-6 sm:space-y-8 xl:space-y-10 pb-8">
    
    <!-- Banner de Alerta em caso de falha de conexão com a API -->
    <div
      v-if="isError"
      class="rounded-xl border border-red-200 bg-red-50 p-4 shadow-xs flex items-center justify-between gap-4 transition-all"
    >
      <div class="flex items-center gap-3">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-red-100 text-red-600 shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div>
          <h4 class="text-sm font-bold text-red-900 font-display">Falha na conexão com a API</h4>
          <p class="text-xs text-red-700">Não foi possível carregar os dados atualizados do VIGITEL. Verifique sua conexão ou se o serviço de backend está ativo.</p>
        </div>
      </div>
      <button
        @click="fetchAllData"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer shrink-0"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
        </svg>
        <span>Tentar Novamente</span>
      </button>
    </div>

    <!-- Seção 1: Visão Geral / Síntese Epidemiológica Hero -->
    <section id="visao-geral" class="scroll-mt-24" aria-label="Visão Geral — Síntese Epidemiológica">
      <HealthGaugeOverview />
    </section>

    <!-- Seção 2: Atividade Física -->
    <section id="atividade-fisica" class="scroll-mt-24">
      <div class="mb-3 sm:mb-4 border-b-2 border-teal pb-1.5">
        <h2 class="text-base sm:text-lg xl:text-xl font-bold tracking-tight text-teal uppercase font-display">Atividade Física</h2>
      </div>
      <SectionAtividadeFisica />
    </section>

    <!-- Seção 3: Sedentarismo -->
    <section id="sedentarismo" class="scroll-mt-24">
      <div class="mb-3 sm:mb-4 border-b-2 border-amber pb-1.5">
        <h2 class="text-base sm:text-lg xl:text-xl font-bold tracking-tight text-amber uppercase font-display">Sedentarismo</h2>
      </div>
      <SectionSedentarismo />
    </section>

    <!-- Seção 4: Desfechos de Saúde -->
    <section id="desfechos" class="scroll-mt-24">
      <div class="mb-3 sm:mb-4 border-b-2 border-red pb-1.5">
        <h2 class="text-base sm:text-lg xl:text-xl font-bold tracking-tight text-red uppercase font-display">Desfechos de Saúde</h2>
      </div>
      <SectionDesfechos />
    </section>

  </div>
</template>

<script setup>
import { useIndicadores } from '../composables/useIndicadores'
import HealthGaugeOverview from '../../visao-geral/components/HealthGaugeOverview.vue'
import SectionAtividadeFisica from '../../atividade-fisica/components/SectionAtividadeFisica.vue'
import SectionSedentarismo from '../../sedentarismo/components/SectionSedentarismo.vue'
import SectionDesfechos from '../../desfechos/components/SectionDesfechos.vue'

const { isError, fetchAllData } = useIndicadores()
</script>
