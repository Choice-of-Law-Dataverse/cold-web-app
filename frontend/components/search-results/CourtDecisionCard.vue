<template>
  <ResultCard :resultData="resultData" cardType="Court Decisions">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
      <!-- Case Title section -->
      <div
        :class="[
          config.gridConfig.caseTitle.columnSpan,
          config.gridConfig.caseTitle.startColumn,
        ]"
      >
        <div class="label-key">{{ getLabel('Case Title') }}</div>
        <div
          :class="[
            config.valueClassMap['Case Title'],
            'text-sm leading-relaxed whitespace-pre-line',
            (!resultData['Case Title'] || resultData['Case Title'] === 'NA') &&
            config.keyLabelPairs.find((pair) => pair.key === 'Case Title')
              ?.emptyValueBehavior?.action === 'display' &&
            !config.keyLabelPairs.find((pair) => pair.key === 'Case Title')
              ?.emptyValueBehavior?.getFallback
              ? 'text-gray-300'
              : '',
          ]"
        >
          {{ getValue('Case Title') }}
        </div>
      </div>

      <!-- Choice of Law Issue section -->
      <div
        :class="[
          config.gridConfig.choiceOfLaw.columnSpan,
          config.gridConfig.choiceOfLaw.startColumn,
        ]"
      >
        <div class="label-key">{{ getLabel('Choice of Law Issue') }}</div>
        <div
          :class="[
            config.valueClassMap['Choice of Law Issue'],
            'text-sm leading-relaxed whitespace-pre-line',
            (!resultData['Choice of Law Issue'] ||
              resultData['Choice of Law Issue'] === 'NA') &&
            config.keyLabelPairs.find(
              (pair) => pair.key === 'Choice of Law Issue'
            )?.emptyValueBehavior?.action === 'display'
              ? 'text-gray-300'
              : '',
          ]"
        >
          {{ getValue('Choice of Law Issue') }}
        </div>
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
import ResultCard from './ResultCard.vue'
import { courtDecisionCardConfig } from '../../config/cardConfigs'

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
})

const config = courtDecisionCardConfig

// Helper functions to get labels and values with fallbacks
const getLabel = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key)
  return pair?.label || key
}

const getValue = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key)
  const value = props.resultData[key]

  if ((!value || value === 'NA') && pair?.emptyValueBehavior) {
    if (pair.emptyValueBehavior.action === 'display') {
      if (pair.emptyValueBehavior.getFallback) {
        return pair.emptyValueBehavior.getFallback(props.resultData)
      }
      return pair.emptyValueBehavior.fallback
    }
    return ''
  }

  return value
}

const getFallbackClass = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key)
  const value = props.resultData[key]

  if (!value && pair?.emptyValueBehavior?.fallbackClass) {
    return pair.emptyValueBehavior.fallbackClass
  }

  return ''
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
