<template>
  <ResultCard :resultData="processedResultData" cardType="Literature">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
      <!-- Title in the 1st column -->
      <div class="md:col-span-5">
        <div class="label-key">{{ keyMap.Title }}</div>
        <div :class="valueClassMap.Title || 'result-value'">
          {{ processedResultData.Title || '[Missing Information]' }}
        </div>
      </div>

      <!-- Author in the 6th column -->
      <div class="md:col-start-6 md:col-span-7">
        <div class="label-key">{{ keyMap.Author }}</div>
        <div :class="valueClassMap.Author || 'result-value'">
          {{ processedResultData.Author || '[Missing Information]' }}
        </div>
        <!-- </div> -->

        <!-- Year in the 7th column -->
        <!-- <div class="md:col-start-7 md:col-span-7"> -->
        <div class="label-key">{{ keyMap.Date }}</div>
        <div :class="valueClassMap.Date || 'result-value'">
          {{ processedResultData.Date || '[Missing Information]' }}
        </div>
        <div class="label-key">{{ keyMap['Publication Title'] }}</div>
        <div :class="valueClassMap['Publication Title'] || 'result-value'">
          {{
            processedResultData['Publication Title'] || '[Missing Information]'
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
    Themes: props.resultData['Themes name'], // Map "Themes name" to "Themes"
  }
})

// Map key labels
const keyMap = {
  Title: 'Title',
  Author: 'Author',
  Date: 'Year',
  'Publication Title': 'Publication',
}

// Map different CSS styles to different typographic components
const valueClassMap = {
  Title: 'result-value-medium',
  Author: 'result-value-small',
  Date: 'result-value-small',
  'Publication Title': 'result-value-small',
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
