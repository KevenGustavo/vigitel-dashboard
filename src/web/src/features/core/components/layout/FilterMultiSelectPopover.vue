<template>
  <div class="flex-1 min-w-[100px]">
    <!-- Trigger Pill -->
    <div
      ref="triggerRef"
      @click="toggle"
      class="flex items-center justify-between bg-white border border-border rounded-lg shadow-2xs hover:border-teal/50 transition-colors cursor-pointer group px-2.5 py-1.5 w-full"
      :class="{ 'border-teal ring-1 ring-teal/20': isOpen }"
      :title="tooltipText"
    >
      <div class="flex items-center gap-1 min-w-0 pr-1">
        <span class="text-[11px] xl:text-[12px] font-medium text-text-muted shrink-0">{{ label }}:</span>
        <span v-if="modelValue.length <= 1" class="text-[12px] xl:text-[13px] font-semibold text-text-primary truncate">
          {{ selectedLabel }}
        </span>
        <span v-else class="inline-flex items-center justify-center min-w-[20px] h-[18px] px-1.5 rounded-full text-[11px] font-bold font-mono bg-teal/15 text-teal shrink-0">
          {{ modelValue.length }}
        </span>
      </div>
      <svg class="h-3.5 w-3.5 shrink-0 text-text-muted group-hover:text-teal transition-colors ml-1" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
      </svg>
    </div>

    <!-- Popover teleportado para o body -->
    <Teleport to="body">
      <div
        v-if="isOpen"
        ref="panelRef"
        class="fixed z-[9999] w-64 rounded-xl border border-border bg-white p-5 shadow-xl cursor-default"
        :style="position"
      >
        <div class="mb-4 flex items-center justify-between">
          <span class="text-sm font-bold text-text-primary font-display">{{ title }}</span>
          <button
            @click.stop="toggleAll"
            class="text-[11px] font-bold text-teal hover:underline bg-teal/10 px-2 py-1.5 rounded-md transition-colors cursor-pointer"
          >
            {{ modelValue.length > 0 ? 'Limpar Seleção' : 'Selecionar Todas' }}
          </button>
        </div>

        <div class="flex flex-col gap-2 max-h-60 overflow-y-auto pr-1">
          <label
            v-for="opt in options"
            :key="opt"
            class="flex items-center gap-2 cursor-pointer group/item"
          >
            <input
              type="checkbox"
              :checked="isSelected(opt)"
              @change="toggleItem(opt)"
              class="w-3.5 h-3.5 rounded border-gray-300 text-teal focus:ring-teal cursor-pointer accent-teal-600"
            >
            <span class="text-[13px] text-text-secondary group-hover/item:text-text-primary transition-colors leading-none">{{ opt }}</span>
          </label>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  options: {
    type: Array,
    default: () => []
  },
  modelValue: {
    type: Array,
    default: () => []
  },
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'toggle', 'close'])

const triggerRef = ref(null)
const panelRef = ref(null)
const position = ref({ top: '0px', left: '0px' })

const selectedLabel = computed(() => {
  if (!props.modelValue || props.modelValue.length === 0) return 'Todas'
  if (props.modelValue.length === 1) return props.modelValue[0]
  return `${props.modelValue.length}`
})

const tooltipText = computed(() => {
  if (!props.modelValue || props.modelValue.length === 0) return `Todas as opções de ${props.title.toLowerCase()}`
  return `${props.title}: ${props.modelValue.join(', ')}`
})

const isSelected = (item) => props.modelValue.includes(item)

const toggleItem = (item) => {
  const current = [...props.modelValue]
  const index = current.indexOf(item)
  if (index === -1) {
    current.push(item)
  } else {
    current.splice(index, 1)
  }
  emit('update:modelValue', current)
}

const toggleAll = () => {
  if (props.modelValue.length > 0) {
    emit('update:modelValue', [])
  } else {
    emit('update:modelValue', [...props.options])
  }
}

const updatePosition = () => {
  if (!triggerRef.value) return
  const rect = triggerRef.value.getBoundingClientRect()
  const width = 256 // w-64
  let left = rect.left
  if (left + width > window.innerWidth - 16) {
    left = Math.max(16, rect.right - width)
  }
  position.value = {
    top: `${rect.bottom + 8}px`,
    left: `${left}px`
  }
}

const toggle = () => {
  updatePosition()
  emit('toggle')
}

const handleClickOutside = (event) => {
  if (props.isOpen) {
    const inTrigger = triggerRef.value?.contains(event.target)
    const inPanel = panelRef.value?.contains(event.target)
    if (!inTrigger && !inPanel) {
      emit('close')
    }
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})
</script>
