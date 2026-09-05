<template>
  <aside class="group flex h-full w-16 shrink-0 flex-col items-center border-r border-border bg-card">
    <!-- Navigation Icons (Scroll & Sections) -->
    <nav class="flex w-full flex-1 flex-col items-center gap-3 py-5">
      
      <!-- Seta para Cima: Navega para a seção anterior ou topo em 1 clique -->
      <button 
        @click="scrollPrev" 
        class="flex h-10 w-10 cursor-pointer items-center justify-center rounded-xl border border-transparent transition-all duration-200 ease-in-out hover:bg-stone-100 hover:border-stone-200 active:scale-95 shadow-2xs" 
        title="Seção Anterior"
        aria-label="Rolar para seção anterior"
      >
        <span class="flex items-center justify-center text-text-muted transition-all duration-150 ease-in-out hover:text-text-primary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5">
            <path d="m18 15-6-6-6 6"/>
          </svg>
        </span>
      </button>

      <!-- Divisor -->
      <div class="my-1 h-[1px] w-6 bg-border/80"></div>

      <!-- Seções Declarativas -->
      <button
        v-for="section in SECTIONS_CONFIG"
        :key="section.id"
        @click="scrollTo(section.id)"
        class="relative flex h-10 w-10 cursor-pointer items-center justify-center rounded-xl transition-all duration-200 ease-in-out"
        :class="activeSection === section.id ? section.activeClass : section.inactiveClass"
        :title="section.title"
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="h-[18px] w-[18px] transition-transform duration-150"
          :class="{ 'scale-110': activeSection === section.id }"
          v-html="section.iconSvg"
        >
        </svg>
      </button>

      <!-- Divisor -->
      <div class="my-1 h-[1px] w-6 bg-border/80"></div>

      <!-- Seta para Baixo: Navega para a próxima seção ou rodapé em 1 clique -->
      <button 
        @click="scrollNext" 
        class="flex h-10 w-10 cursor-pointer items-center justify-center rounded-xl border border-transparent transition-all duration-200 ease-in-out hover:bg-stone-100 hover:border-stone-200 active:scale-95 shadow-2xs" 
        title="Próxima Seção"
        aria-label="Rolar para próxima seção"
      >
        <span class="flex items-center justify-center text-text-muted transition-all duration-150 ease-in-out hover:text-text-primary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5">
            <path d="m6 9 6 6 6-6"/>
          </svg>
        </span>
      </button>

    </nav>
  </aside>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const SECTIONS_CONFIG = [
  {
    id: 'visao-geral',
    title: 'Visão Geral',
    activeClass: 'bg-stone-100 text-stone-900 font-bold border-l-3 border-stone-800 shadow-2xs',
    inactiveClass: 'text-text-muted hover:bg-stone-50 hover:text-text-primary',
    iconSvg: '<rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/>'
  },
  {
    id: 'atividade-fisica',
    title: 'Atividade Física',
    activeClass: 'bg-teal/15 text-teal font-bold border-l-3 border-teal shadow-2xs',
    inactiveClass: 'text-stone-400 hover:bg-teal/5 hover:text-teal',
    iconSvg: '<circle cx="18.5" cy="17.5" r="3.5"/><circle cx="5.5" cy="17.5" r="3.5"/><circle cx="15" cy="5" r="1"/><path d="M12 17.5V14l-3-3 4-3 2 3h2"/>'
  },
  {
    id: 'sedentarismo',
    title: 'Sedentarismo',
    activeClass: 'bg-amber/15 text-amber font-bold border-l-3 border-amber shadow-2xs',
    inactiveClass: 'text-stone-400 hover:bg-amber/5 hover:text-amber',
    iconSvg: '<rect x="2" y="7" width="20" height="15" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/>'
  },
  {
    id: 'desfechos',
    title: 'Desfechos de Saúde',
    activeClass: 'bg-rose-50 text-rose-600 font-bold border-l-3 border-rose-600 shadow-2xs',
    inactiveClass: 'text-stone-400 hover:bg-rose-50/50 hover:text-rose-600',
    iconSvg: '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M12 5 9.04 9h5.92L12 13"/>'
  }
]

const SECTIONS = SECTIONS_CONFIG.map(s => s.id)
const activeSection = ref('visao-geral')
let isManualScrolling = false
let manualScrollTimer = null

const updateActiveSection = () => {
  if (isManualScrolling) return

  const mainContent = document.getElementById('main-content')
  if (!mainContent) return

  if (mainContent.scrollTop < 60) {
    activeSection.value = 'visao-geral'
    return
  }

  if (mainContent.scrollHeight - mainContent.scrollTop - mainContent.clientHeight < 50) {
    activeSection.value = 'desfechos'
    return
  }

  const mainRect = mainContent.getBoundingClientRect()

  for (let i = SECTIONS.length - 1; i >= 0; i--) {
    const el = document.getElementById(SECTIONS[i])
    if (el) {
      const elRect = el.getBoundingClientRect()
      if (elRect.top - mainRect.top <= 220) {
        activeSection.value = SECTIONS[i]
        return
      }
    }
  }

  activeSection.value = 'visao-geral'
}

const scrollTo = (target) => {
  const mainContent = document.getElementById('main-content')
  if (!mainContent) return

  isManualScrolling = true
  if (manualScrollTimer) clearTimeout(manualScrollTimer)

  if (target === 'top' || target === 'visao-geral') {
    activeSection.value = 'visao-geral'
    mainContent.scrollTo({ top: 0, behavior: 'smooth' })
  } else if (target === 'bottom') {
    activeSection.value = 'desfechos'
    mainContent.scrollTo({ top: mainContent.scrollHeight, behavior: 'smooth' })
  } else {
    const el = document.getElementById(target)
    if (el) {
      activeSection.value = target
      const mainRect = mainContent.getBoundingClientRect()
      const elRect = el.getBoundingClientRect()
      const targetScroll = mainContent.scrollTop + (elRect.top - mainRect.top) - 16
      mainContent.scrollTo({ top: Math.max(0, targetScroll), behavior: 'smooth' })
    }
  }

  manualScrollTimer = setTimeout(() => {
    isManualScrolling = false
    updateActiveSection()
  }, 700)
}

const scrollPrev = () => {
  const currentIndex = SECTIONS.indexOf(activeSection.value)
  if (currentIndex > 0) {
    scrollTo(SECTIONS[currentIndex - 1])
  } else {
    scrollTo('top')
  }
}

const scrollNext = () => {
  const currentIndex = SECTIONS.indexOf(activeSection.value)
  if (currentIndex < SECTIONS.length - 1) {
    scrollTo(SECTIONS[currentIndex + 1])
  } else {
    scrollTo('bottom')
  }
}

onMounted(() => {
  const mainContent = document.getElementById('main-content')
  if (mainContent) {
    mainContent.addEventListener('scroll', updateActiveSection, { passive: true })
    setTimeout(updateActiveSection, 150)
  }
})

onUnmounted(() => {
  const mainContent = document.getElementById('main-content')
  if (mainContent) {
    mainContent.removeEventListener('scroll', updateActiveSection)
  }
  if (manualScrollTimer) clearTimeout(manualScrollTimer)
})
</script>
