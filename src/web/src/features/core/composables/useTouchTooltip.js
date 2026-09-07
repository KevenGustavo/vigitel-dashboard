import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Composable para permitir que popovers explicativos e tooltips funcionem
 * perfeitamente tanto com toque no celular/tablet quanto com hover de mouse no desktop.
 */
export function useTouchTooltip() {
  const isOpen = ref(false)

  const toggle = (event) => {
    if (event) {
      event.stopPropagation()
    }
    isOpen.value = !isOpen.value
  }

  const close = () => {
    isOpen.value = false
  }

  const open = () => {
    isOpen.value = true
  }

  const handleWindowClick = () => {
    isOpen.value = false
  }

  onMounted(() => {
    if (typeof window !== 'undefined') {
      window.addEventListener('click', handleWindowClick)
    }
  })

  onUnmounted(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('click', handleWindowClick)
    }
  })

  return {
    isOpen,
    toggle,
    close,
    open
  }
}
