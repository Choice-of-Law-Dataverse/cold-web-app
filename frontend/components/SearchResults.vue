<template>
  <div class="container">
    <div class="col-span-12">
      <!-- Flexbox Container -->
      <div class="filters-header mb-6">
        <!-- Types Filter -->
        <SearchFilters :options="typeOptions" v-model="currentTypeFilter" />

        <!-- Themes Filter -->
        <SearchFilters :options="themeOptions" v-model="currentThemeFilter" />
        <h2 class="text-right">{{ props.totalMatches }} Results</h2>
      </div>

      <!-- Results Grid -->
      <div class="results-grid">
        <div
          v-for="(resultData, key) in allResults"
          :key="key"
          class="result-item"
        >
          <component
            :is="getResultComponent(resultData.source_table)"
            :resultData="resultData"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import LegislationCard from '@/components/LegislationCard.vue'
import CourtDecisionCard from '@/components/CourtDecisionCard.vue'
import AnswerCard from '@/components/AnswerCard.vue'
import ResultCard from '@/components/ResultCard.vue'
import SearchFilters from './SearchFilters.vue'

const getResultComponent = (source_table) => {
  switch (source_table) {
    case 'Legislation':
      return LegislationCard
    case 'Court decisions':
      return CourtDecisionCard
    case 'Answers':
      return AnswerCard
    default:
      return ResultCard
  }
}

// Props to receive current filter values
const props = defineProps({
  data: {
    type: Object,
    default: () => ({ tables: {} }), // Default to an object with an empty tables field
  },
  filters: {
    type: Object,
    required: true,
  },
  totalMatches: {
    type: Number,
    default: 0,
  },
})

// Gather all results
const allResults = computed(() => {
  return Object.values(props.data?.tables || {}) // Fallback to an empty object
})

const emit = defineEmits(['update:filters'])

const typeOptions = [
  'All Types',
  'Court Decisions',
  'Legal Instruments',
  'Questions',
]
const themeOptions = [
  'All Themes',
  'Party Autonomy',
  'Express and Tacit Choice',
  'Arbitration',
]

// Reactive states initialized from props
const currentTypeFilter = ref(props.filters.type || 'All Types')
const currentThemeFilter = ref(props.filters.theme || 'All Themes')

// Watch for changes in either filter and emit them up
watch([currentTypeFilter, currentThemeFilter], ([newType, newTheme]) => {
  emit('update:filters', { type: newType, theme: newTheme })
})

// Watch for prop changes to re-sync dropdowns when parent updates
watch(
  () => props.filters,
  (newFilters) => {
    currentTypeFilter.value = newFilters.type || 'All Types'
    currentThemeFilter.value = newFilters.theme || 'All Themes'
  },
  { deep: true, immediate: true }
)
</script>

<style scoped>
.filters-header {
  display: flex;
  align-items: center; /* Vertically align items */
  justify-content: space-between; /* Space between SearchFilters and h2 */
  padding-bottom: 12px;
}

.filters-header h2 {
  margin: 0; /* Remove default margin for better alignment */
  padding-bottom: 0; /* Override inline padding if needed */
}
</style>
