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
        <UCard>
          <!-- Conditional rendering based on the type of search result -->

          <!-- Display for Answers -->
          <template v-if="isAnswer(resultData)">
            <div style="position: relative">
              <!-- Position the "Open" link in the top right corner -->
              <NuxtLink
                :to="`/question/${resultData.id}`"
                style="position: absolute; top: 10px; right: 10px"
              >
                Open
              </NuxtLink>
              <div v-for="(resultKey, index) in answerKeys" :key="resultKey">
                <div class="result-key">{{ keyMap[resultKey] }}</div>
                <div
                  :class="[
                    'result-value',
                    { 'no-margin': index === answerKeys.length - 1 },
                  ]"
                >
                  <template v-if="resultKey === 'Legal provision articles'">
                    <div v-if="resultData[resultKey]">
                      <span
                        v-for="(item, index) in resultData[resultKey].split(
                          ','
                        )"
                        :key="index"
                        style="margin-right: 10px"
                      >
                        <NuxtLink
                          :to="`/legal-instrument/${item.trim().split(' ')[0]}#${item.trim().split(' ').slice(1).join('')}`"
                        >
                          {{ item.trim() }}
                        </NuxtLink>
                      </span>
                    </div>
                    <div v-else>No legal provision</div>
                  </template>
                  <template v-else>
                    {{ resultData[resultKey] }}
                  </template>
                </div>
              </div>
            </div>
          </template>

          <!-- Display for Court decisions -->
          <template v-else-if="isCourtDecision(resultData)">
            <div style="position: relative">
              <!-- Position the "Open" link in the top right corner -->
              <NuxtLink
                :to="`/court-decision/${resultData.id}`"
                style="position: absolute; top: 10px; right: 10px"
              >
                Open
              </NuxtLink>
              <div v-for="resultKey in courtDecisionKeys" :key="resultKey">
                <div class="result-key">{{ keyMap[resultKey] }}</div>
                <div class="result-value">
                  <template v-if="resultKey === 'Choice of law issue'">
                    {{ resultData[resultKey] || '[Missing Information]' }}
                  </template>
                  <template v-else>
                    <span>{{ resultData[resultKey] }}</span>
                  </template>
                </div>
              </div>
            </div>
          </template>

          <!-- Display for Legislation -->
          <template v-else-if="isLegislation(resultData)">
            <div style="position: relative">
              <NuxtLink
                :to="`/legal-instrument/${resultData.id}`"
                style="position: absolute; top: 10px; right: 10px"
              >
                Open
              </NuxtLink>

              <!-- Legislation details -->
              <div
                v-for="legislationKey in legislationKeys"
                :key="legislationKey"
              >
                <div class="result-key">{{ keyMap[legislationKey] }}</div>
                <div class="result-value">
                  {{ resultData[legislationKey] || '[Missing Information]' }}
                </div>
              </div>
            </div>
          </template>
        </UCard>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

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
