<template>
  <ResultCard :resultData="resultData" cardType="Answers">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
      <!-- Question section -->
      <div
        :class="[
          config.gridConfig.question.columnSpan,
          config.gridConfig.question.startColumn,
        ]"
      >
        <div class="label-key">{{ getLabel('Question') }}</div>
        <div
          :class="[
            config.valueClassMap.Question,
            'text-sm leading-relaxed whitespace-pre-line',
            (!resultData.Question || resultData.Question === 'NA') &&
            config.keyLabelPairs.find((pair) => pair.key === 'Question')
              ?.emptyValueBehavior?.action === 'display'
              ? 'text-gray-300'
              : '',
          ]"
        >
          {{ getValue('Question') }}
        </div>
      </div>

      <!-- Answer section -->
      <div
        :class="[
          config.gridConfig.answer.columnSpan,
          config.gridConfig.answer.startColumn,
        ]"
      >
        <div class="label-key">{{ getLabel('Answer') }}</div>
        <div
          :class="[
            config.getAnswerClass(resultData.Answer),
            'text-sm leading-relaxed whitespace-pre-line',
            (!resultData.Answer || resultData.Answer === 'NA') &&
            config.keyLabelPairs.find((pair) => pair.key === 'Answer')
              ?.emptyValueBehavior?.action === 'display'
              ? 'text-gray-300'
              : '',
          ]"
        >
          {{ getValue('Answer') }}
        </div>
      </div>

      <!-- More Information section -->
      <div
        :class="[
          config.gridConfig.source.columnSpan,
          config.gridConfig.source.startColumn,
        ]"
      >
        <div class="label-key">{{ getLabel('More Information') }}</div>
        <ul class="result-value-small">
          <li>{{ getValue('More Information') }}</li>
          <li>{{ domesticValue }}</li>
          <li>{{ relatedCasesCount }} related court decisions</li>
        </ul>
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed } from 'vue'
import ResultCard from './ResultCard.vue'
import { answerCardConfig } from '../../config/cardConfigs'

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
})

const config = answerCardConfig

// Computed property to display the number of related cases
const relatedCasesCount = computed(() => {
  const links = props.resultData['Court Decisions Link']
  if (!links) return 0
  return links.split(',').filter((link) => link.trim() !== '').length
})

// Updated computed property for fallback between keys
const domesticValue = computed(() => {
  return props.resultData['Domestic Legal Provisions'] != null
    ? getValue('Domestic Legal Provisions')
    : props.resultData['Domestic Instruments ID'] != null
      ? getValue('Domestic Instruments ID')
      : getValue('Jurisdictions Literature ID')
})

// Helper functions to get labels and values with fallbacks
const getLabel = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key)
  return pair?.label || key
}

const getValue = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key)
  const value = props.resultData[key]

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
.answer-card-grid {
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

.result-value-small li {
  list-style-type: disc; /* Forces bullet points */
  margin-left: 20px; /* Ensures proper indentation */
}
</style>
