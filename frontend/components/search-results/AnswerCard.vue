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
        v-if="hasMoreInformation"
        :class="[
          config.gridConfig.source.columnSpan,
          config.gridConfig.source.startColumn,
        ]"
      >
        <div class="label-key">{{ getLabel('More Information') }}</div>
        <ul class="result-value-small">
          <li v-if="resultData['More Information']">
            {{ getValue('More Information') }}
          </li>
          <li v-if="hasDomesticValue">{{ domesticValue }}</li>
          <li v-if="relatedCasesCount">
            <a :href="relatedDecisionsLink"
              >{{ relatedCasesCount }} related court decisions</a
            >
          </li>
        </ul>
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { useRuntimeConfig } from '#imports' // new import
import ResultCard from './ResultCard.vue'
import { answerCardConfig } from '../../config/cardConfigs'

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
})

const config = answerCardConfig

const runtimeConfig = useRuntimeConfig() // new
const literatureTitle = ref(null) // initialize as null to indicate "not yet loaded"

// Updated function to fetch literature title using table "Literature"
async function fetchLiteratureTitle(id) {
  try {
    const response = await fetch(
      `${runtimeConfig.public.apiBaseUrl}/search/details`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${runtimeConfig.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ table: 'Literature', id }),
      }
    )
    if (!response.ok) throw new Error('Failed to fetch literature title')
    const data = await response.json()
    // Use the key 'Title' from the API response
    const title = data['Title']
    literatureTitle.value = title && title !== 'NA' ? title : id
  } catch (err) {
    console.error('Error fetching literature title:', err)
    literatureTitle.value = id
  }
}

// Use a watcher that triggers immediately
watch(
  () => props.resultData['Jurisdictions Literature ID'],
  (newId) => {
    if (newId) fetchLiteratureTitle(newId)
  },
  { immediate: true }
)

// Updated computed property for fallback between keys
const domesticValue = computed(() => {
  if (props.resultData['Domestic Legal Provisions'] != null) {
    return getValue('Domestic Legal Provisions')
  } else if (props.resultData['Domestic Instruments ID'] != null) {
    return getValue('Domestic Instruments ID')
  } else if (props.resultData['Jurisdictions Literature ID'] != null) {
    // If literatureTitle is still null, show a loading message; otherwise use the value
    return literatureTitle.value === null ? 'Loading...' : literatureTitle.value
  } else {
    return ''
  }
})

// Computed property to display the number of related cases
const relatedCasesCount = computed(() => {
  const links = props.resultData['Court Decisions Link']
  if (!links) return 0
  return links.split(',').filter((link) => link.trim() !== '').length
})

// Updated computed property for the related court decisions link
const relatedDecisionsLink = computed(() => {
  const id = props.resultData['id']
  return `question/${id}#related-court-decisions`
})

// New computed property to conditionally show domesticValue bullet
const hasDomesticValue = computed(() => {
  return (
    props.resultData['Domestic Legal Provisions'] ||
    props.resultData['Domestic Instruments ID'] ||
    props.resultData['Jurisdictions Literature ID']
  )
})

const hasMoreInformation = computed(() => {
  return (
    props.resultData['More Information'] ||
    hasDomesticValue.value ||
    relatedCasesCount.value > 0
  )
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
