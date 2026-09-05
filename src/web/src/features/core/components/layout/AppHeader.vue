<template>
  <header class="bg-surface border-b border-border">
    <!-- Linha Superior: Logo e Título -->
    <div class="px-8 py-5 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <!-- Ícone do App -->
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-teal to-emerald-600 shadow-sm">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-6 w-6 text-white">
            <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
            <path d="M3 10h2.5l2-3.5 3 8 2.5-4.5 1.5 2.5H21" />
          </svg>
        </div>
        <div class="flex flex-col">
          <h1 class="text-[22px] font-bold leading-[1.2] tracking-[-0.02em] text-text-primary font-display">
            <span class="text-teal">VIGITEL</span> Atividade & Saúde
          </h1>
          <p class="text-[13px] font-semibold uppercase tracking-[0.06em] text-text-muted font-display">
            Monitoramento Epidemiológico
          </p>
        </div>
      </div>
      
      <!-- Ação Global: Exportar Dados com Menu Especializado em Saúde -->
      <div class="relative" ref="exportDropdownContainer">
        <button
          @click.stop="isExportMenuOpen = !isExportMenuOpen"
          class="flex items-center gap-2 text-xs xl:text-sm font-semibold text-text-primary hover:text-teal bg-white hover:bg-teal/5 transition-all px-3 py-1.5 rounded-lg border border-border hover:border-teal/30 shadow-2xs cursor-pointer group"
          :class="{ 'border-teal ring-2 ring-teal/15 text-teal': isExportMenuOpen }"
          title="Exportar dados para análise epidemiológica e estatística"
        >
          <svg class="h-4 w-4 text-text-muted group-hover:text-teal transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <span>Exportar Dados</span>
          <svg class="h-3.5 w-3.5 text-text-muted group-hover:text-teal transition-transform duration-200" :class="{ 'rotate-180 text-teal': isExportMenuOpen }" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
          </svg>
        </button>

        <!-- Menu Popover de Exportação -->
        <Transition
          enter-active-class="transition duration-100 ease-out"
          enter-from-class="transform scale-95 opacity-0"
          enter-to-class="transform scale-100 opacity-100"
          leave-active-class="transition duration-75 ease-in"
          leave-from-class="transform scale-100 opacity-100"
          leave-to-class="transform scale-95 opacity-0"
        >
          <div
            v-if="isExportMenuOpen"
            class="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-border p-2 z-50 text-left font-sans cursor-default"
            @click.stop
          >
            <div class="px-3 py-2 border-b border-border mb-1.5">
              <p class="text-xs font-bold text-text-primary font-display">Exportação de Dados VIGITEL</p>
              <p class="text-[11px] text-text-muted">Selecione o formato ideal para a sua análise:</p>
            </div>

            <!-- Opção 1: Relatório Epidemiológico CSV (Excel) -->
            <button
              @click="handleExport('csv-epidemiologico')"
              class="w-full flex items-start gap-2.5 p-2 rounded-lg hover:bg-teal/10 transition-colors text-left group/opt cursor-pointer"
            >
              <div class="w-7 h-7 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center justify-center shrink-0 mt-0.5 group-hover/opt:bg-emerald-600 group-hover/opt:text-white transition-colors">
                <span class="text-[10px] font-bold font-mono">XLS</span>
              </div>
              <div class="min-w-0">
                <div class="text-xs font-semibold text-text-primary group-hover/opt:text-teal flex items-center gap-1.5">
                  <span>Relatório Epidemiológico</span>
                  <span class="text-[9px] font-bold bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded">Recomendado</span>
                </div>
                <p class="text-[11px] text-text-muted leading-tight mt-0.5">
                  CSV formatado para Excel (com UTF-8 BOM e ';') com metadados do SUS, resumo de indicadores e tabelas clínicas.
                </p>
              </div>
            </button>

            <!-- Opção 2: Série Histórica Tidy CSV (R / SPSS / Python) -->
            <button
              @click="handleExport('csv-tidy')"
              class="w-full flex items-start gap-2.5 p-2 rounded-lg hover:bg-teal/10 transition-colors text-left group/opt cursor-pointer mt-1"
            >
              <div class="w-7 h-7 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200 flex items-center justify-center shrink-0 mt-0.5 group-hover/opt:bg-indigo-600 group-hover/opt:text-white transition-colors">
                <span class="text-[10px] font-bold font-mono">CSV</span>
              </div>
              <div class="min-w-0">
                <div class="text-xs font-semibold text-text-primary group-hover/opt:text-teal">
                  Série Histórica Tabular (Tidy)
                </div>
                <p class="text-[11px] text-text-muted leading-tight mt-0.5">
                  Formato longo (1 linha por observação) ideal para R, Python (Pandas), SPSS, Stata e modelagem estatística.
                </p>
              </div>
            </button>

            <!-- Opção 3: JSON Estruturado -->
            <button
              @click="handleExport('json')"
              class="w-full flex items-start gap-2.5 p-2 rounded-lg hover:bg-teal/10 transition-colors text-left group/opt cursor-pointer mt-1"
            >
              <div class="w-7 h-7 rounded-md bg-stone-100 text-stone-600 border border-stone-300 flex items-center justify-center shrink-0 mt-0.5 group-hover/opt:bg-stone-700 group-hover/opt:text-white transition-colors">
                <span class="text-[10px] font-bold font-mono">{ }</span>
              </div>
              <div class="min-w-0">
                <div class="text-xs font-semibold text-text-primary group-hover/opt:text-teal">
                  Dados Brutos (JSON)
                </div>
                <p class="text-[11px] text-text-muted leading-tight mt-0.5">
                  Payload completo serializado para programadores, scripts automatizados e integrações de API.
                </p>
              </div>
            </button>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Linha Inferior: Barra de Filtros Responsiva -->
    <div class="bg-[#f8fafc] border-t border-border px-6 xl:px-8 py-2.5 flex items-center gap-2 xl:gap-3 w-full overflow-x-auto filters-scroll">
      
      <!-- Label "Filtros:" -->
      <div class="flex items-center gap-1.5 mr-1 shrink-0">
        <svg class="h-4 w-4 text-teal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        <span class="text-xs xl:text-sm font-bold text-text-secondary hidden sm:inline">Filtros:</span>
      </div>

      <!-- Container das 6 Pills em Grid Flexível Reativo -->
      <div class="flex-1 flex items-center gap-1.5 xl:gap-2.5 min-w-0">
        
        <!-- 1. Período -->
        <div 
          ref="yearDropdownContainer" 
          @click="toggleDropdown('year')"
          class="flex-1 min-w-[125px] flex items-center justify-between bg-white border border-border rounded-lg shadow-2xs hover:border-teal/50 transition-colors cursor-pointer group px-2.5 py-1.5"
          :class="{ 'border-teal ring-1 ring-teal/20': isYearDropdownOpen }"
          title="Período: 2006 a 2024"
        >
          <div class="flex items-center gap-1.5 min-w-0 pr-1">
            <span class="text-[11px] xl:text-[12px] font-medium text-text-muted shrink-0">Anos:</span>
            <span class="text-[12px] xl:text-[13px] font-bold text-text-primary font-mono tracking-tight shrink-0">
              {{ selectedMin }}–{{ selectedMax }}
            </span>
          </div>
          <svg class="h-3.5 w-3.5 shrink-0 text-text-muted group-hover:text-teal transition-colors ml-1" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
          </svg>
        </div>

        <!-- 2. Capitais -->
        <div 
          ref="cityDropdownContainer" 
          @click="toggleDropdown('city')"
          class="flex-1 min-w-[105px] flex items-center justify-between bg-white border border-border rounded-lg shadow-2xs hover:border-teal/50 transition-colors cursor-pointer group px-2.5 py-1.5"
          :class="{ 'border-teal ring-1 ring-teal/20': isCityDropdownOpen }"
          :title="state.capitais.length > 0 ? 'Capitais: ' + state.capitais.join(', ') : 'Todas as 27 capitais'"
        >
          <div class="flex items-center gap-1 min-w-0 pr-1">
            <span class="text-[11px] xl:text-[12px] font-medium text-text-muted shrink-0">Capitais:</span>
            <span v-if="state.capitais.length <= 1" class="text-[12px] xl:text-[13px] font-semibold text-text-primary truncate">
              {{ selectedCityLabel }}
            </span>
            <span v-else class="inline-flex items-center justify-center min-w-[20px] h-[18px] px-1.5 rounded-full text-[11px] font-bold font-mono bg-teal/15 text-teal shrink-0">
              {{ state.capitais.length }}
            </span>
          </div>
          <svg class="h-3.5 w-3.5 shrink-0 text-text-muted group-hover:text-teal transition-colors ml-1" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
          </svg>
        </div>

        <!-- 3. Sexo -->
        <div 
          ref="sexDropdownContainer" 
          @click="toggleDropdown('sex')"
          class="flex-1 min-w-[95px] flex items-center justify-between bg-white border border-border rounded-lg shadow-2xs hover:border-teal/50 transition-colors cursor-pointer group px-2.5 py-1.5"
          :class="{ 'border-teal ring-1 ring-teal/20': isSexDropdownOpen }"
          title="Filtro por Sexo Biológico"
        >
          <div class="flex items-center gap-1 min-w-0 pr-1">
            <span class="text-[11px] xl:text-[12px] font-medium text-text-muted shrink-0">Sexo:</span>
            <span class="text-[12px] xl:text-[13px] font-semibold text-text-primary truncate">
              {{ state.sexo }}
            </span>
          </div>
          <svg class="h-3.5 w-3.5 shrink-0 text-text-muted group-hover:text-teal transition-colors ml-1" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
          </svg>
        </div>

        <!-- 4. Faixa Etária (Componente Reutilizável) -->
        <FilterMultiSelectPopover
          label="Idade"
          title="Faixas Etárias"
          :options="filterOptions?.faixas_etarias || []"
          v-model="state.faixa_etaria"
          :isOpen="isAgeDropdownOpen"
          @toggle="toggleDropdown('age')"
          @close="isAgeDropdownOpen = false"
        />

        <!-- 5. Escolaridade (Componente Reutilizável) -->
        <FilterMultiSelectPopover
          label="Escola"
          title="Escolaridade"
          :options="filterOptions?.escolaridades || []"
          v-model="state.escolaridade"
          :isOpen="isEducationDropdownOpen"
          @toggle="toggleDropdown('education')"
          @close="isEducationDropdownOpen = false"
        />

        <!-- 6. Raça/Cor (Componente Reutilizável) -->
        <FilterMultiSelectPopover
          label="Raça"
          title="Raça/Cor"
          :options="filterOptions?.racas_cores || []"
          v-model="state.raca_cor"
          :isOpen="isRaceDropdownOpen"
          @toggle="toggleDropdown('race')"
          @close="isRaceDropdownOpen = false"
        />

      </div>

      <!-- Botão Limpar Filtros Geral -->
      <button 
        @click="clearAllFilters" 
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border transition-all duration-150 cursor-pointer shrink-0 shadow-2xs group"
        :class="hasActiveFilters 
          ? 'border-red-200 bg-red-50 text-red-600 hover:bg-red-100 hover:border-red-300 font-semibold shadow-xs' 
          : 'border-border bg-white text-text-muted hover:text-text-primary hover:bg-stone-100 font-normal'"
        title="Restaurar todos os filtros para os padrões nacionais (2006–2024)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5 transition-transform duration-300" :class="hasActiveFilters ? 'text-red-500 group-hover:rotate-180' : 'text-text-muted'">
          <path fill-rule="evenodd" d="M4 2a1 1 0 0 1 1 1v2.101a7.002 7.002 0 0 1 11.601 2.566 1 1 0 1 1-1.885.666A5.002 5.002 0 0 0 5.999 7H9a1 1 0 0 1 0 2H4a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1Zm.008 9.057a1 1 0 0 1 1.276.61A5.002 5.002 0 0 0 14.001 13H11a1 1 0 1 1 0-2h5a1 1 0 0 1 1 1v5a1 1 0 1 1-2 0v-2.101a7.002 7.002 0 0 1-11.601-2.566 1 1 0 0 1 .61-1.276Z" clip-rule="evenodd" />
        </svg>
        <span class="text-xs">Limpar Filtros</span>
      </button>

    </div>
  </header>

  <!-- ═══════════════════════════════════════════════════════════════
       Popovers Específicos Teleportados para o <body>
       ═══════════════════════════════════════════════════════════════ -->

  <!-- Popover: Período (Slider) -->
  <Teleport to="body">
    <div v-if="isYearDropdownOpen" ref="yearPopoverPanel"
      class="fixed z-[9999] w-72 rounded-xl border border-border bg-white p-5 shadow-xl cursor-default"
      :style="popoverPos.year">
      <div class="mb-5 flex items-center justify-between">
        <span class="text-sm font-bold text-text-primary font-display">Período Analisado</span>
        <span class="text-xs font-bold text-teal bg-teal/10 px-2 py-1 rounded-md font-mono">{{ selectedMin }} a {{ selectedMax }}</span>
      </div>
      
      <!-- Slider Wrapper -->
      <div class="relative h-1.5 w-full rounded-full bg-gray-200 mt-6 mb-5">
        <!-- Active Track -->
        <div 
          class="absolute h-full rounded-full bg-teal pointer-events-none"
          :style="{
            left: `${((selectedMin - minYear) / (maxYear - minYear)) * 100}%`,
            width: `${((selectedMax - selectedMin) / (maxYear - minYear)) * 100}%`
          }"
        ></div>
        
        <!-- Input 1 -->
        <input 
          type="range" 
          :min="minYear" 
          :max="maxYear" 
          v-model.number="state.ano_inicio" 
          class="absolute -top-[5px] w-full appearance-none bg-transparent pointer-events-none custom-range outline-none"
        />
        <!-- Input 2 -->
        <input 
          type="range" 
          :min="minYear" 
          :max="maxYear" 
          v-model.number="state.ano_fim" 
          class="absolute -top-[5px] w-full appearance-none bg-transparent pointer-events-none custom-range outline-none"
        />
      </div>
      
      <div class="flex justify-between text-xs font-semibold text-text-muted mt-2 font-mono">
        <span>{{ minYear }}</span>
        <span>{{ maxYear }}</span>
      </div>
    </div>
  </Teleport>

  <!-- Popover: Capitais -->
  <Teleport to="body">
    <div v-if="isCityDropdownOpen" ref="cityPopoverPanel"
      class="fixed z-[9999] w-[600px] rounded-xl border border-border bg-white p-5 shadow-xl cursor-default"
      :style="popoverPos.city">
      <div class="mb-5 flex items-center justify-between">
        <span class="text-sm font-bold text-text-primary font-display">Capitais Selecionadas</span>
        <button @click.stop="toggleAllCities" class="text-[11px] font-bold text-teal hover:underline bg-teal/10 px-2 py-1.5 rounded-md transition-colors cursor-pointer">
          {{ state.capitais.length > 0 ? 'Limpar Seleção' : 'Selecionar Todas' }}
        </button>
      </div>
      
      <div class="grid grid-cols-3 gap-6">
        <div v-for="(cidades, regiao) in cidadesPorRegiao" :key="regiao" class="flex flex-col">
          <div class="flex items-center justify-between mb-2">
             <span class="text-[11px] font-bold uppercase tracking-wider text-text-muted">{{ regiao }}</span>
             <button @click.stop="toggleRegion(regiao)" class="text-[10px] font-bold text-teal hover:underline cursor-pointer">
               {{ isRegionAllSelected(regiao) ? 'Limpar' : 'Selecionar' }}
             </button>
          </div>
          <div class="flex flex-col gap-1.5">
            <label v-for="cidade in cidades" :key="cidade.nome_cidade" class="flex items-center gap-2 cursor-pointer group/item">
              <input 
                type="checkbox" 
                :checked="isCitySelected(cidade.nome_cidade)" 
                @change="toggleCity(cidade.nome_cidade)" 
                class="w-3.5 h-3.5 rounded border-gray-300 text-teal focus:ring-teal cursor-pointer accent-teal-600"
              >
              <span class="text-[13px] text-text-secondary group-hover/item:text-text-primary transition-colors leading-none">{{ cidade.nome_cidade }}</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Popover: Sexo -->
  <Teleport to="body">
    <div v-if="isSexDropdownOpen" ref="sexPopoverPanel"
      class="fixed z-[9999] w-48 rounded-xl border border-border bg-white p-4 shadow-xl cursor-default"
      :style="popoverPos.sex">
      <span class="block text-sm font-bold text-text-primary mb-3 font-display">Sexo</span>
      <div class="flex flex-col gap-1">
        <button 
          @click="selectSex('Ambos')" 
          :class="['text-left px-3 py-2 rounded-md text-[13px] transition-colors cursor-pointer', state.sexo === 'Ambos' ? 'bg-teal/10 text-teal font-bold' : 'text-text-secondary hover:bg-gray-100']">
          Ambos
        </button>
        <button 
          v-for="sexo in filterOptions?.sexos" 
          :key="sexo" 
          @click="selectSex(sexo)" 
          :class="['text-left px-3 py-2 rounded-md text-[13px] transition-colors cursor-pointer', state.sexo === sexo ? 'bg-teal/10 text-teal font-bold' : 'text-text-secondary hover:bg-gray-100']">
          {{ sexo }}
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { onMounted, onUnmounted, ref, reactive, computed } from 'vue'
import { useFilters } from '../../composables/useFilters'
import { useIndicadores } from '../../composables/useIndicadores'
import FilterMultiSelectPopover from './FilterMultiSelectPopover.vue'
import {
  generateEpidemiologicalCsv,
  generateTidyDatasetCsv,
  generateRawJson,
  downloadFile
} from '../../../../utils/exporter'

const { state, resetFilters } = useFilters()
const {
  filterOptions,
  visaoGeral,
  desfechos,
  atividadeFisica,
  sedentarismo,
  evolucaoAtividadeFisica,
  evolucaoSedentarismo,
  evolucaoDesfechos,
  comparativoSexo,
  sedentarismoFaixaEtaria,
  rankingCidades,
  indicadorRanking
} = useIndicadores()

const hasActiveFilters = computed(() => {
  return (
    state.ano_inicio !== 2006 ||
    state.ano_fim !== 2024 ||
    (state.capitais && state.capitais.length > 0) ||
    (state.sexo && state.sexo !== 'Ambos') ||
    (state.faixa_etaria && state.faixa_etaria.length > 0) ||
    (state.escolaridade && state.escolaridade.length > 0) ||
    (state.raca_cor && state.raca_cor.length > 0)
  )
})

// ═══════════════════════════════════════════════════════════════
// Posicionamento dos Popovers (Teleport)
// ═══════════════════════════════════════════════════════════════
const popoverPos = reactive({
  year: { top: '0px', left: '0px' },
  city: { top: '0px', left: '0px' },
  sex: { top: '0px', left: '0px' }
})

const calcPos = (containerRef, popoverWidth = 256) => {
  if (!containerRef?.value) return { top: '0px', left: '0px' }
  const rect = containerRef.value.getBoundingClientRect()
  let left = rect.left
  if (left + popoverWidth > window.innerWidth - 16) {
    left = Math.max(16, rect.right - popoverWidth)
  }
  return {
    top: `${rect.bottom + 8}px`,
    left: `${left}px`
  }
}

// ─── Estados dos Dropdowns ─────────────────────────────
const isYearDropdownOpen = ref(false)
const yearDropdownContainer = ref(null)
const yearPopoverPanel = ref(null)

const isCityDropdownOpen = ref(false)
const cityDropdownContainer = ref(null)
const cityPopoverPanel = ref(null)

const isSexDropdownOpen = ref(false)
const sexDropdownContainer = ref(null)
const sexPopoverPanel = ref(null)

const isAgeDropdownOpen = ref(false)
const isEducationDropdownOpen = ref(false)
const isRaceDropdownOpen = ref(false)

const toggleDropdown = (name) => {
  const currentStates = {
    year: isYearDropdownOpen,
    city: isCityDropdownOpen,
    sex: isSexDropdownOpen,
    age: isAgeDropdownOpen,
    education: isEducationDropdownOpen,
    race: isRaceDropdownOpen
  }

  // Fecha todos os outros dropdowns
  Object.keys(currentStates).forEach(key => {
    if (key !== name) currentStates[key].value = false
  })

  // Alterna o selecionado
  if (currentStates[name]) {
    currentStates[name].value = !currentStates[name].value
  }

  // Atualiza posição se abriu
  if (name === 'year' && isYearDropdownOpen.value) {
    popoverPos.year = calcPos(yearDropdownContainer, 288)
  } else if (name === 'city' && isCityDropdownOpen.value) {
    popoverPos.city = calcPos(cityDropdownContainer, 600)
  } else if (name === 'sex' && isSexDropdownOpen.value) {
    popoverPos.sex = calcPos(sexDropdownContainer, 192)
  }
}

const closeAllDropdowns = () => {
  isYearDropdownOpen.value = false
  isCityDropdownOpen.value = false
  isSexDropdownOpen.value = false
  isAgeDropdownOpen.value = false
  isEducationDropdownOpen.value = false
  isRaceDropdownOpen.value = false
}

// ─── Lógica do Slider de Anos ─────────────────────────────
const minYear = computed(() => filterOptions.value?.anos ? Math.min(...filterOptions.value.anos) : 2006)
const maxYear = computed(() => filterOptions.value?.anos ? Math.max(...filterOptions.value.anos) : 2024)

const selectedMin = computed(() => Math.min(state.ano_inicio, state.ano_fim))
const selectedMax = computed(() => Math.max(state.ano_inicio, state.ano_fim))

// ─── Lógica do Filtro de Cidades (Multi-Select) ───────────
const REGION_MAPPING = {
  'Rio Branco': 'Norte', 'Macapá': 'Norte', 'Manaus': 'Norte', 'Belém': 'Norte', 'Porto Velho': 'Norte', 'Boa Vista': 'Norte', 'Palmas': 'Norte',
  'Maceió': 'Nordeste', 'Salvador': 'Nordeste', 'Fortaleza': 'Nordeste', 'São Luís': 'Nordeste', 'João Pessoa': 'Nordeste', 'Recife': 'Nordeste', 'Teresina': 'Nordeste', 'Natal': 'Nordeste', 'Aracaju': 'Nordeste',
  'Brasília': 'Centro-Oeste', 'Goiânia': 'Centro-Oeste', 'Cuiabá': 'Centro-Oeste', 'Campo Grande': 'Centro-Oeste',
  'Vitória': 'Sudeste', 'Belo Horizonte': 'Sudeste', 'São Paulo': 'Sudeste', 'Rio de Janeiro': 'Sudeste',
  'Curitiba': 'Sul', 'Porto Alegre': 'Sul', 'Florianópolis': 'Sul'
}

const cidadesPorRegiao = computed(() => {
  const grupos = { 'Norte': [], 'Nordeste': [], 'Centro-Oeste': [], 'Sudeste': [], 'Sul': [] }
  if (filterOptions.value?.cidades) {
    filterOptions.value.cidades.forEach(c => {
      const regiao = REGION_MAPPING[c.nome_cidade] || 'Outros'
      if (grupos[regiao]) grupos[regiao].push(c)
    })
  }
  return grupos
})

const toggleCity = (nome_cidade) => {
  const index = state.capitais.indexOf(nome_cidade)
  if (index === -1) {
    state.capitais.push(nome_cidade)
  } else {
    state.capitais.splice(index, 1)
  }
}

const isCitySelected = (nome_cidade) => state.capitais.includes(nome_cidade)

const toggleRegion = (regiao) => {
  const cidadesDaRegiao = cidadesPorRegiao.value[regiao].map(c => c.nome_cidade)
  const allSelected = cidadesDaRegiao.every(id => state.capitais.includes(id))
  
  if (allSelected) {
    state.capitais = state.capitais.filter(id => !cidadesDaRegiao.includes(id))
  } else {
    cidadesDaRegiao.forEach(id => {
      if (!state.capitais.includes(id)) state.capitais.push(id)
    })
  }
}

const isRegionAllSelected = (regiao) => {
  if (!cidadesPorRegiao.value[regiao]) return false
  const cidadesDaRegiao = cidadesPorRegiao.value[regiao].map(c => c.nome_cidade)
  if (cidadesDaRegiao.length === 0) return false
  return cidadesDaRegiao.every(id => state.capitais.includes(id))
}

const toggleAllCities = () => {
  if (state.capitais.length > 0) {
    state.capitais = []
  } else {
    state.capitais = filterOptions.value?.cidades?.map(c => c.nome_cidade) || []
  }
}

const selectedCityLabel = computed(() => {
  if (!state.capitais || state.capitais.length === 0) return 'Todas'
  if (state.capitais.length === 1) return state.capitais[0]
  return `${state.capitais.length}`
})

// ─── Lógica do Filtro de Sexo ─────────────────────────────
const selectSex = (sexo) => {
  state.sexo = sexo
  isSexDropdownOpen.value = false
}

const clearAllFilters = () => {
  closeAllDropdowns()
  resetFilters(minYear.value, maxYear.value)
}

// ─── Exportação Especializada de Dados do Dashboard ───────
const isExportMenuOpen = ref(false)
const exportDropdownContainer = ref(null)

const handleExport = (format) => {
  isExportMenuOpen.value = false
  const dateStr = new Date().toISOString().slice(0, 10)

  const dashboardData = {
    visaoGeral: visaoGeral.value,
    desfechos: desfechos.value,
    atividadeFisica: atividadeFisica.value,
    sedentarismo: sedentarismo.value,
    evolucaoAtividadeFisica: evolucaoAtividadeFisica.value,
    evolucaoSedentarismo: evolucaoSedentarismo.value,
    evolucaoDesfechos: evolucaoDesfechos.value,
    comparativoSexo: comparativoSexo.value,
    sedentarismoFaixaEtaria: sedentarismoFaixaEtaria.value,
    rankingCidades: rankingCidades.value,
    indicadorRanking: indicadorRanking.value
  }

  if (format === 'csv-epidemiologico') {
    const csv = generateEpidemiologicalCsv(dashboardData, state)
    downloadFile(csv, `vigitel-relatorio-epidemiologico-${dateStr}.csv`, 'text/csv;charset=utf-8;')
  } else if (format === 'csv-tidy') {
    const csv = generateTidyDatasetCsv(dashboardData, state)
    downloadFile(csv, `vigitel-serie-historica-tidy-${dateStr}.csv`, 'text/csv;charset=utf-8;')
  } else if (format === 'json') {
    const json = generateRawJson(dashboardData, state)
    downloadFile(json, `vigitel-dados-completos-${dateStr}.json`, 'application/json;charset=utf-8;')
  }
}

// ─── Manipulador de Clique Fora (Click Outside) ───────────
const handleClickOutside = (event) => {
  if (isExportMenuOpen.value && exportDropdownContainer.value && !exportDropdownContainer.value.contains(event.target)) {
    isExportMenuOpen.value = false
  }

  const check = (isOpen, containerRef, panelRef) => {
    if (isOpen.value) {
      const inContainer = containerRef.value?.contains(event.target)
      const inPanel = panelRef.value?.contains(event.target)
      if (!inContainer && !inPanel) {
        isOpen.value = false
      }
    }
  }
  check(isYearDropdownOpen, yearDropdownContainer, yearPopoverPanel)
  check(isCityDropdownOpen, cityDropdownContainer, cityPopoverPanel)
  check(isSexDropdownOpen, sexDropdownContainer, sexPopoverPanel)
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
  
  if (filterOptions.value?.anos && filterOptions.value.anos.length > 0) {
    const apiMin = Math.min(...filterOptions.value.anos)
    const apiMax = Math.max(...filterOptions.value.anos)
    if (state.ano_inicio === 2006 && state.ano_fim === 2024) {
      state.ano_inicio = apiMin
      state.ano_fim = apiMax
    }
  }
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})
</script>

<style scoped>
.filters-scroll::-webkit-scrollbar {
  height: 6px;
}
.filters-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.filters-scroll::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}
.filters-scroll::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}

.custom-range::-webkit-slider-thumb {
  pointer-events: auto;
  appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background-color: #14b8a6;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
  cursor: grab;
  position: relative;
  z-index: 10;
}
.custom-range::-webkit-slider-thumb:active {
  cursor: grabbing;
  transform: scale(1.1);
}
.custom-range::-moz-range-thumb {
  pointer-events: auto;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background-color: #14b8a6;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
  cursor: grab;
  position: relative;
  z-index: 10;
}
.custom-range::-moz-range-thumb:active {
  cursor: grabbing;
  transform: scale(1.1);
}
</style>
