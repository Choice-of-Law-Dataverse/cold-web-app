<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <DetailDisplay
          :loading="loading"
          :resultData="processedAnswerData"
          :keyLabelPairs="filteredKeyLabelPairs"
          :valueClassMap="valueClassMap"
          formattedSourceTable="Question"
        >
          <!-- Custom rendering for Legal provision articles -->
          <template #domestic-legal-provisions="{ value }">
            <QuestionSourceList
              :sources="
                [
                  ...(value ||
                  processedAnswerData?.['Domestic Legal Provisions'] ||
                  processedAnswerData?.['Jurisdictions Literature ID']
                    ? [
                        value ||
                          processedAnswerData?.['Domestic Legal Provisions'] ||
                          processedAnswerData?.['Jurisdictions Literature ID'],
                      ]
                    : []),
                ].filter(Boolean)
              "
              :fallbackData="processedAnswerData"
              :valueClassMap="valueClassMap"
              :noLinkList="[
                processedAnswerData?.['Jurisdictions Literature ID'],
              ]"
              :fetchOupChapter="true"
              :fetchPrimarySource="true"
            />
          </template>

          <!-- Custom rendering for Court Decisions ID -->
          <template #court-decisions-id="{ value }">
            <CourtDecisionRenderer
              :value="value"
              :valueClassMap="valueClassMap['Court Decisions ID']"
            />
          </template>

          <!-- Related Literature -->
          <template #related-literature>
            <RelatedLiterature
              :themes="processedAnswerData?.Themes || ''"
              :valueClassMap="valueClassMap['Related Literature']"
            />
          </template>
        </DetailDisplay>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import DetailDisplay from '~/components/ui/BaseDetailDisplay.vue'
import CourtDecisionRenderer from '~/components/legal/CourtDecisionRenderer.vue'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'
import QuestionSourceList from '~/components/sources/QuestionSourceList.vue'

const route = useRoute() // Access the route to get the ID param
const answerData = ref(null) // Store fetched court decision data
const loading = ref(true) // Track loading state

const config = useRuntimeConfig()

async function fetchAnswer(id) {
  const jsonPayload = {
    table: 'Answers',
    id: id,
  }

  try {
    const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jsonPayload),
    })

    if (!response.ok) throw new Error('Failed to fetch answer')

    answerData.value = await response.json()
  } catch (error) {
    console.error('Error fetching answer:', error)
  } finally {
    loading.value = false
  }
}

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Question', label: 'Question' },
  { key: 'Answer', label: 'Answer' },
  { key: 'More Information', label: 'More Information' },
  {
    key: 'Domestic Legal Provisions',
    label: 'Source',
  },
  { key: 'Court Decisions ID', label: 'related cases' },
  { key: 'Related Literature', label: '' },
]

const valueClassMap = {
  Question: 'result-value-medium',
  Answer: 'result-value-large',
  'Domestic Legal Provisions': 'result-value-small',
  'Court Decisions ID': 'result-value-small',
}

// Preprocess data to handle custom rendering cases
const processedAnswerData = computed(() => {
  if (!answerData.value) return null
  return {
    ...answerData.value,
    'Domestic Legal Provisions':
      answerData.value['Domestic Legal Provisions'] || '',
    'Court Decisions ID': answerData.value['Court Decisions ID']
      ? answerData.value['Court Decisions ID']
          .split(',')
          .map((caseId) => caseId.trim())
      : [],
  }
})

const filteredKeyLabelPairs = computed(() => {
  if (!processedAnswerData.value) return keyLabelPairs

  const caseIds = processedAnswerData.value['Court Decisions ID']
  const hasRelatedCases = Array.isArray(caseIds) && caseIds.length > 0

  return keyLabelPairs.filter((pair) => {
    if (pair.key === 'Court Decisions ID') {
      return hasRelatedCases
    }
    return true
  })
})

onMounted(() => {
  const id = route.params.id
  fetchAnswer(id).then(() => {
    if (answerData.value?.Themes) {
    }
  })
})
</script>
