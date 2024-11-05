<template>
  <div class="container">
    <div class="col-span-12">
      <h2 style="text-align: right; padding-bottom: 50px">
        {{ props.totalMatches }} Results
      </h2>
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
import { computed } from 'vue'

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
</script>
