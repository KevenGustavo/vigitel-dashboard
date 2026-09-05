<template>
  <div class="flex h-screen w-full bg-surface overflow-hidden">
    <!-- Sidebar fixa na esquerda -->
    <AppSidebar />

    <!-- Área principal -->
    <div class="flex flex-1 flex-col overflow-hidden">
      <!-- Header com Logo e Filtros -->
      <header class="z-10">
        <AppHeader />
      </header>

      <!-- Conteúdo das Páginas -->
      <main class="flex-1 overflow-y-auto" id="main-content">
        <div class="mx-auto max-w-7xl px-8 pt-4 pb-8">
          <Dashboard />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import AppSidebar from './features/core/components/layout/AppSidebar.vue'
import AppHeader from './features/core/components/layout/AppHeader.vue'
import Dashboard from './features/core/views/Dashboard.vue'
</script>

<style>
/* Transição suave entre páginas */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
