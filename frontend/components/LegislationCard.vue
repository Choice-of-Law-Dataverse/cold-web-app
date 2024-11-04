<template>
  <ResultCard :resultData="resultData" cardType="Legislation">
    <div class="legislation-card-grid">
      <!-- Abbreviation in the 1st column -->
      <div class="grid-item" style="grid-column: 1 / span 5">
        <div class="label-key">{{ keyMap.Abbreviation }}</div>
        <div :class="valueClassMap.Abbreviation || 'result-value'">
          {{ resultData.Abbreviation || '[Missing Information]' }}
        </div>
      </div>

      <!-- Title in the 6th column -->
      <div class="grid-item" style="grid-column: 6 / span 7">
        <div class="label-key">{{ keyMap['Title (in English)'] }}</div>
        <div :class="valueClassMap['Title (in English)'] || 'result-value'">
          {{ resultData['Title (in English)'] || '[Missing Information]' }}
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

const legislationKeys = ['Abbreviation', 'Title (in English)']

const keyMap = {
  'Title (in English)': 'Title',
  Abbreviation: 'Abbreviation',
}

// Map different CSS styles to different typographic components
const valueClassMap = {
  'Title (in English)': 'result-value-small',
  Abbreviation: 'result-value-medium',
}
</script>

<style scoped>
.legislation-card-grid {
  display: grid;
  grid-template-columns: repeat(12, var(--column-width));
  column-gap: var(--gutter-width);
  align-items: start;
}

.grid-item {
  display: flex;
  flex-direction: column;
  gap: 4px; /* Space between key and value */
}
</style>
