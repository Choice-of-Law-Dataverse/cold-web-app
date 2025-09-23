<template>
  <ResultCard :result-data="resultData" card-type="Court Decisions">
    <div class="grid grid-cols-1 gap-6 md:grid-cols-12">
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
            'whitespace-pre-line text-sm leading-relaxed',
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

      <!-- Date section -->
      <div
        v-if="
          resultData['Publication Date ISO'] &&
          resultData['Publication Date ISO'] !== 'NA'
        "
        :class="[
          config.gridConfig.date.columnSpan,
          config.gridConfig.date.startColumn,
        ]"
      >
        <div class="label-key">{{ getLabel('Publication Date ISO') }}</div>
        <div
          :class="[
            config.valueClassMap['Publication Date ISO'],
            'whitespace-pre-line text-sm leading-relaxed',
          ]"
        >
          {{ getValue('Publication Date ISO') }}
        </div>
      </div>

      <!-- Instance section -->
      <div
        v-if="resultData['Instance'] && resultData['Instance'] !== 'NA'"
        :class="[
          config.gridConfig.instance.columnSpan,
          config.gridConfig.instance.startColumn,
        ]"
      >
        <div class="label-key">{{ getLabel('Instance') }}</div>
        <div
          :class="[
            config.valueClassMap['Instance'],
            'whitespace-pre-line text-sm leading-relaxed',
          ]"
        >
          {{ getValue('Instance') }}
        </div>
      </div>

      <!-- Choice of Law Issue section -->
      <div
        v-if="
          resultData['Choice of Law Issue'] &&
          resultData['Choice of Law Issue'] !== 'NA'
        "
        :class="[
          config.gridConfig.choiceOfLaw.columnSpan,
          config.gridConfig.choiceOfLaw.startColumn,
        ]"
      >
        <div class="label-key">{{ getLabel('Choice of Law Issue') }}</div>
        <div
          :class="[
            config.valueClassMap['Choice of Law Issue'],
            'whitespace-pre-line text-sm leading-relaxed',
          ]"
        >
          {{ getValue('Choice of Law Issue') }}
        </div>
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
import ResultCard from '@/components/search-results/ResultCard.vue'
import { courtDecisionCardConfig } from '@/config/cardConfigs'
import { extractYear } from '@/utils/format'

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
})

const config = courtDecisionCardConfig

const getLabel = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key)
  return pair?.label || key
}

const getValue = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key)
  let value = props.resultData[key]

  // Apply extractYear to 'Publication Date ISO' if a valid value exists
  if (key === 'Publication Date ISO' && value && value !== 'NA') {
    value = extractYear(value)
  }

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
