<template>
  <ResultCard :resultData="resultData" cardType="Answers">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
      <!-- Question section -->
      <div :class="`md:col-span-${config.gridConfig.question.columnSpan} md:col-start-${config.gridConfig.question.startColumn}`">
        <div class="label-key">{{ getLabel('Question') }}</div>
        <div :class="[
          config.valueClassMap.Question,
          'text-sm leading-relaxed whitespace-pre-line',
          (!resultData.Question || resultData.Question === 'NA') && config.keyLabelPairs.find(pair => pair.key === 'Question')?.emptyValueBehavior?.action === 'display' ? 'text-gray-300' : ''
        ]">
          {{ getValue('Question') }}
        </div>
      </div>

      <!-- Answer section -->
      <div :class="`md:col-span-${config.gridConfig.answer.columnSpan} md:col-start-${config.gridConfig.answer.startColumn}`">
        <div class="label-key">{{ getLabel('Answer') }}</div>
        <div :class="[
          config.getAnswerClass(resultData.Answer),
          'text-sm leading-relaxed whitespace-pre-line',
          (!resultData.Answer || resultData.Answer === 'NA') && config.keyLabelPairs.find(pair => pair.key === 'Answer')?.emptyValueBehavior?.action === 'display' ? 'text-gray-300' : ''
        ]">
          {{ getValue('Answer') }}
        </div>
      </div>

      <!-- Source section -->
      <div
        v-if="resultData.Answer !== 'No data'"
        :class="`md:col-span-${config.gridConfig.source.columnSpan} md:col-start-${config.gridConfig.source.startColumn}`"
      >
        <div class="label-key">{{ getLabel('Legal provision articles') }}</div>
        <ul class="result-value-small">
          <template v-if="resultData['Literature Title']">
            <li>{{ resultData['Literature Title'] }}</li>
          </template>
          <template v-if="resultData['Legal Provision Articles']">
            <li>{{ resultData['Legal Provision Articles'] }}</li>
          </template>
          <template v-else-if="resultData['Legislation-ID']">
            <li>{{ resultData['Legislation-ID'] }}</li>
          </template>
          <template v-else-if="resultData['More Information']">
            <li>{{ resultData['More Information'] }}</li>
          </template>
        </ul>
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
import ResultCard from './ResultCard.vue'
import { answerCardConfig } from '../../config/cardConfigs'

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
})

const config = answerCardConfig

// Helper functions to get labels and values with fallbacks
const getLabel = (key) => {
  const pair = config.keyLabelPairs.find(pair => pair.key === key)
  return pair?.label || key
}

const getValue = (key) => {
  const pair = config.keyLabelPairs.find(pair => pair.key === key)
  const value = props.resultData[key]
  
  if (!value && pair?.emptyValueBehavior) {
    if (pair.emptyValueBehavior.action === 'display') {
      return pair.emptyValueBehavior.fallback
    }
    return ''
  }
  
  return value
}

const getFallbackClass = (key) => {
  const pair = config.keyLabelPairs.find(pair => pair.key === key)
  const value = props.resultData[key]
  
  if (!value && pair?.emptyValueBehavior?.fallbackClass) {
    return pair.emptyValueBehavior.fallbackClass
  }
  
  return ''
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
