<template>
  <ResultCard :resultData="resultData" cardType="Court Decisions">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
      <!-- Case Title in the 1st column -->
      <div class="md:col-span-4">
        <div class="label-key">{{ keyMap['Case Title'] }}</div>
        <div :class="valueClassMap['Case Title'] || 'result-value'">
          {{ caseTitle }}
        </div>
      </div>

      <!-- Choice of Law Issue in the 6th column -->
      <div class="md:col-start-6 md:col-span-6">
        <div class="label-key">{{ keyMap['Choice of Law Issue'] }}</div>
        <div :class="valueClassMap['Choice of Law Issue'] || 'result-value'">
          {{ resultData['Choice of Law Issue'] || '[Missing Information]' }}
        </div>
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed } from 'vue'
import ResultCard from './ResultCard.vue'

// Props
const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
})

// Compute a fallback for "Case Title"
const caseTitle = computed(() => {
  if (!props.resultData) return '[Missing Information]'
  const title = props.resultData['Case Title'] || ''
  // If the title is "Not found", use "Case Citation"
  return title.trim() === 'Not found'
    ? props.resultData['Case Citation'] || '[Missing Information]'
    : title || '[Missing Information]'
})

// Define the keys and mappings specific to court decisions
const courtDecisionKeys = ['Case Title', 'Choice of Law Issue']
const keyMap = {
  'Case Title': 'Case Title',
  'Choice of Law Issue': 'Choice of Law Issue',
}

// Map different CSS styles to different typographic components
const valueClassMap = {
  'Case Title': 'result-value-medium',
  'Choice of Law Issue': 'result-value-small',
}
</script>

<style scoped>
.court-decision-grid {
  display: grid;
  grid-template-columns: repeat(12, var(--column-width));
  column-gap: var(--gutter-width);
  align-items: start;
}

.grid-item {
  display: flex;
  flex-direction: column;
}

.label-key {
  @extend .label;
  padding: 0;
  margin-top: 12px;
}
</style>
