<template>
  <ResultCard :resultData="processedResultData" cardType="Legal Instrument">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
      <!-- Abbreviation in the 1st column -->
      <div class="md:col-span-5">
        <div class="label-key">{{ keyMap['Title (in English)'] }}</div>
        <div :class="valueClassMap['Title (in English)'] || 'result-value'">
          {{
            processedResultData['Title (in English)'] || '[Missing Information]'
          }}
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

// Computed property to process the result data
const processedResultData = computed(() => {
  if (!props.resultData) return null

  return {
    ...props.resultData,
    Themes: props.resultData['Domestic Legal Provisions Themes'], // Map "Themes name" to "Themes"
  }
})

// Map key labels
const keyMap = {
  'Title (in English)': 'Title',
  Abbreviation: 'Abbreviation',
}

// Map different CSS styles to different typographic components
const valueClassMap = {
  'Title (in English)': 'result-value-medium',
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
}

.label-key {
  @extend .label;
  padding: 0;
  margin-top: 12px;
}
</style>
