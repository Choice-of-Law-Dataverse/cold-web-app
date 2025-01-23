<template>
  <ResultCard :resultData="resultData" cardType="Court decisions">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
      <!-- Case Title in the 1st column -->
      <div class="md:col-span-4">
        <div class="label-key">{{ keyMap.Case }}</div>
        <div :class="valueClassMap.Case || 'result-value'">
          {{ resultData.Case || '[Missing Information]' }}
        </div>
      </div>

      <!-- Choice of Law Issue in the 6th column -->
      <div class="md:col-start-6 md:col-span-6">
        <div class="label-key">{{ keyMap['Choice of law issue'] }}</div>
        <div :class="valueClassMap['Choice of law issue'] || 'result-value'">
          {{ resultData['Choice of law issue'] || '[Missing Information]' }}
        </div>
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
// Props
const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
})

// Define the keys and mappings specific to court decisions
const courtDecisionKeys = ['Case', 'Choice of law issue']
const keyMap = {
  Case: 'Case Title',
  'Choice of law issue': 'Choice of Law Issue',
}

// Map different CSS styles to different typographic components
const valueClassMap = {
  Case: 'result-value-medium',
  'Choice of law issue': 'result-value-small',
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
