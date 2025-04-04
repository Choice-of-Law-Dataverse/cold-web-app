<template>
  <ResultCard :resultData="processedResultData" cardType="Literature">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
      <!-- Title section -->
      <div :class="`md:col-span-${config.gridConfig.title.columnSpan} md:col-start-${config.gridConfig.title.startColumn}`">
        <div class="label-key">{{ getLabel('Title') }}</div>
        <div :class="[
          config.valueClassMap.Title,
          'text-sm leading-relaxed whitespace-pre-line',
          (!processedResultData.Title || processedResultData.Title === 'NA') && config.keyLabelPairs.find(pair => pair.key === 'Title')?.emptyValueBehavior?.action === 'display' ? 'text-gray-300' : ''
        ]">
          {{ getValue('Title') }}
        </div>
      </div>

      <!-- Author and Year section -->
      <div :class="`md:col-span-${config.gridConfig.authorYear.columnSpan} md:col-start-${config.gridConfig.authorYear.startColumn}`">
        <div class="grid grid-cols-2 gap-4">
          <!-- Author -->
          <div>
            <div class="label-key">{{ getLabel('Author') }}</div>
            <div :class="[
              config.valueClassMap.Author,
              'text-sm leading-relaxed whitespace-pre-line',
              (!processedResultData.Author || processedResultData.Author === 'NA') && config.keyLabelPairs.find(pair => pair.key === 'Author')?.emptyValueBehavior?.action === 'display' ? 'text-gray-300' : ''
            ]">
              {{ getValue('Author') }}
            </div>
          </div>
          <!-- Year -->
          <div>
            <div class="label-key">{{ getLabel('Publication Year') }}</div>
            <div :class="[
              config.valueClassMap['Publication Year'],
              'text-sm leading-relaxed whitespace-pre-line',
              (!processedResultData['Publication Year'] || processedResultData['Publication Year'] === 'NA') && config.keyLabelPairs.find(pair => pair.key === 'Publication Year')?.emptyValueBehavior?.action === 'display' ? 'text-gray-300' : ''
            ]">
              {{ getValue('Publication Year') }}
            </div>
          </div>
        </div>

        <!-- Publication section -->
        <div class="mt-4">
          <template v-if="shouldDisplay('Publication Title')">
            <div class="label-key">{{ getLabel('Publication Title') }}</div>
            <div :class="[
              config.valueClassMap['Publication Title'],
              'text-sm leading-relaxed whitespace-pre-line',
              (!processedResultData['Publication Title'] || processedResultData['Publication Title'] === 'NA') && config.keyLabelPairs.find(pair => pair.key === 'Publication Title')?.emptyValueBehavior?.action === 'display' ? 'text-gray-300' : ''
            ]">
              {{ getValue('Publication Title') }}
            </div>
          </template>
          <template v-else-if="shouldDisplay('Publisher')">
            <div class="label-key">{{ getLabel('Publisher') }}</div>
            <div :class="[
              config.valueClassMap['Publisher'],
              'text-sm leading-relaxed whitespace-pre-line',
              (!processedResultData['Publisher'] || processedResultData['Publisher'] === 'NA') && config.keyLabelPairs.find(pair => pair.key === 'Publisher')?.emptyValueBehavior?.action === 'display' ? 'text-gray-300' : ''
            ]">
              {{ getValue('Publisher') }}
            </div>
          </template>
        </div>
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed } from 'vue'
import ResultCard from './ResultCard.vue'
import { literatureCardConfig } from '../../config/cardConfigs'

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
})

const config = literatureCardConfig

// Process the result data using the config's processData function
const processedResultData = computed(() => {
  return config.processData(props.resultData)
})

// Helper functions to get labels and values with fallbacks
const getLabel = (key) => {
  const pair = config.keyLabelPairs.find(pair => pair.key === key)
  return pair?.label || key
}

const shouldDisplay = (key) => {
  const pair = config.keyLabelPairs.find(pair => pair.key === key)
  if (!pair?.emptyValueBehavior?.shouldDisplay) return true
  return pair.emptyValueBehavior.shouldDisplay(processedResultData.value)
}

const getValue = (key) => {
  const pair = config.keyLabelPairs.find(pair => pair.key === key)
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
.literature-card-grid {
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
