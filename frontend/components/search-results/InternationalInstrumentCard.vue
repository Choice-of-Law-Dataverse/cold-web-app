<template>
  <ResultCard
    :resultData="processedResultData"
    cardType="International Instrument"
  >
    <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
      <!-- Title section -->
      <div
        :class="[
          config.gridConfig.title.columnSpan,
          config.gridConfig.title.startColumn,
        ]"
      >
        <div class="label-key">{{ getLabel('Name') }}</div>
        <div
          :class="[
            config.valueClassMap['Name'],
            'text-sm leading-relaxed whitespace-pre-line',
            (!processedResultData['Name'] ||
              processedResultData['Name'] === 'NA') &&
            config.keyLabelPairs.find((pair) => pair.key === 'Name')
              ?.emptyValueBehavior?.action === 'display'
              ? 'text-gray-300'
              : '',
          ]"
        >
          {{ getValue('Name') }}
        </div>
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed } from 'vue'
import ResultCard from './ResultCard.vue'
import { internationalInstrumentCardConfig } from '../../config/cardConfigs'

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
})

const config = {
  ...internationalInstrumentCardConfig,
  gridConfig: {
    title: {
      columnSpan: 'md:col-span-12',
      startColumn: 'md:col-start-1',
    },
  },
}

const processedResultData = computed(() => {
  // If you have a processData function for international instruments, use it here
  return props.resultData
})

const getLabel = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key)
  return pair?.label || key
}

const getValue = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key)
  const value = processedResultData.value?.[key]
  if (!value && pair?.emptyValueBehavior) {
    if (pair.emptyValueBehavior.action === 'display') {
      return pair.emptyValueBehavior.fallback
    }
    return ''
  }
  return value
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
