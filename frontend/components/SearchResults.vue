<template>
  <div class="container">
    <div class="col-span-12">
      <!-- Flexbox Container -->
      <div class="filters-header flex items-center justify-between mb-6">
        <SearchFilters v-model="currentFilter" />
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

// Define props and assign them to a variable
const props = defineProps({
  data: {
    type: Object,
    default: () => ({ tables: {} }), // Provide default value for data
  },
  totalMatches: {
    type: Number,
    default: 0,
  },
})

// Gather all results
const allResults = computed(() => {
  return Object.values(props.data.tables)
})

const emit = defineEmits(['filter-updated'])

const currentFilter = defineModel('filter', { default: 'All Types' }) // Two-way binding

// Watch for changes and emit them up to parent
watch(currentFilter, (newFilter) => {
  emit('filter-updated', newFilter)
})
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
