<template>
  <UModal
    :model-value="modelValue"
    @update:model-value="(v) => $emit('update:modelValue', v)"
  >
    <div class="p-4">
      <h3 class="text-lg font-semibold mb-2">Cite this entry</h3>
      <p class="text-sm text-gray-700 leading-relaxed break-words">
        {{ citationText }}
      </p>
    </div>
  </UModal>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

defineProps({
  modelValue: { type: Boolean, default: false },
})
defineEmits(['update:modelValue'])

const route = useRoute()

const pageTitle = ref('')
const currentURL = ref('')

onMounted(() => {
  // Safely access browser APIs on client
  pageTitle.value = typeof document !== 'undefined' ? document.title || '' : ''
  currentURL.value = typeof window !== 'undefined' ? window.location.href : ''
})

function slugToPageType(slug) {
  switch (slug) {
    case 'jurisdiction':
      return 'Jurisdiction'
    case 'court-decision':
      return 'Court Decision'
    case 'domestic-instrument':
      return 'Domestic Instrument'
    case 'regional-instrument':
      return 'Regional Instrument'
    case 'international-instrument':
      return 'International Instrument'
    case 'arbitral-rule':
      return 'Arbitral Rule'
    case 'arbitral-award':
      return 'Arbitral Award'
    case 'literature':
      return 'Literature'
    case 'question':
      return 'Question'
    default: {
      // Generic title-case fallback
      if (!slug) return 'Page'
      return slug
        .split('-')
        .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
        .join(' ')
    }
  }
}

const pageType = computed(() => {
  const segments = route.path.split('/').filter(Boolean)
  return slugToPageType(segments[0] || '')
})

const year = computed(() => new Date().getFullYear())
const monthYear = computed(() => {
  const d = new Date()
  const month = d.toLocaleString('en-US', { month: 'long' })
  return `${month} ${d.getFullYear()}`
})

const citationText = computed(() => {
  const title = pageTitle.value || 'Choice of Law Dataverse'
  const url = currentURL.value
  return `${title}. Choice of Law Dataverse (${year.value}). ${pageType.value} (${monthYear.value}). Licensed under CC BY-SA. Available at: ${url}`
})
</script>
