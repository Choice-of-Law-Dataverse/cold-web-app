<template>
  <UContainer
    style="
      margin-top: 50px;
      width: 80%;
      max-width: 1200px;
      margin-left: auto;
      margin-right: auto;
    "
  >
    <p style="text-align: right; padding-bottom: 50px">
      {{ props.totalMatches }} Results
    </p>
    <div class="results-grid">
      <div
        v-for="(resultData, key) in allResults"
        :key="key"
        class="result-item"
      >
        <component
          :is="getResultComponent(resultData.source_table)"
          :resultData="resultData"
        />
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

import LegislationCard from '@/components/LegislationCard.vue'
import CourtDecisionCard from '@/components/CourtDecisionCard.vue'
import AnswerCard from '@/components/AnswerCard.vue'
import ResultCard from '@/components/ResultCard.vue'

const getResultComponent = (source_table) => {
  switch (source_table) {
    case 'Legislation':
      return LegislationCard
    case 'Court decisions':
      return CourtDecisionCard
    case 'Answers':
      return AnswerCard
    default:
      return ResultCard
  }
}

// Define props and assign them to a variable
const props = defineProps({
  data: {
    type: Object,
    default: () => ({ tables: {} }), // Provide default value for data
  },
  totalMatches: {
    type: Number,
    default: 0,
  },
})

// Define the keys and their order for "Answers"
const answerKeys = [
  'Name (from Jurisdiction)',
  'source_table',
  'Themes',
  'Questions',
  'Answer',
  'Legal provision articles',
]

// Define the keys and their order for "Court decisions"
const courtDecisionKeys = [
  'Jurisdiction Names',
  'source_table',
  'Themes',
  'Case',
  'Choice of law issue',
]

// Define the keys and their order for "Legal Instrument"
const legislationKeys = [
  'Jurisdiction name',
  'source_table',
  'Abbreviation',
  'Title (in English)',
]

// Define a keyMap to rename the keys for display
const keyMap = {
  // Answers
  Answer: 'ANSWER',
  'Name (from Jurisdiction)': 'JURISDICTION',
  Questions: 'QUESTION',
  'Legal provision articles': 'SOURCE',
  // Court Decisions
  Case: 'CASE TITLE',
  'Jurisdiction Names': 'JURISDICTION',
  'Choice of law issue': 'CHOICE OF LAW ISSUE',
  // Legislations
  'Title (in English)': 'TITLE',
  'Jurisdiction name': 'JURISDICTION',
  Abbreviation: 'Abbreviation',
}

// Gather all results
const allResults = computed(() => {
  return Object.values(props.data.tables)
})

// Utility functions

function isAnswer(resultData) {
  return resultData.source_table === 'Answers'
}

function isCourtDecision(resultData) {
  return resultData.source_table === 'Court decisions'
}

function isLegislation(resultData) {
  return resultData.source_table === 'Legislation'
}
</script>
