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
          <template #legal-provision-articles="{ value }">
            <QuestionSourceList
              :sources="
                [
                  ...(value ||
                  processedAnswerData?.['Legislation-ID'] ||
                  processedAnswerData?.['More information']
                    ? [
                        value ||
                          processedAnswerData?.['Legislation-ID'] ||
                          processedAnswerData?.['More information'],
                      ]
                    : []),
                  processedAnswerData?.['Name (from Jurisdiction)'],
                ].filter(Boolean)
              "
              :fallbackData="processedAnswerData"
              :valueClassMap="valueClassMap"
              :noLinkList="[processedAnswerData?.['More information']]"
            />
          </template>

          <!-- Custom rendering for Case ID -->
          <template #case-id="{ value }">
            <div>
              <ul v-if="Array.isArray(value) && value.length">
                <li
                  v-for="(caseId, index) in value"
                  :key="index"
                  :class="valueClassMap['Case ID'] || 'result-value-small'"
                >
                  <CourtCaseLink :caseId="caseId" />
                </li>
              </ul>

              <div v-else>
                <span :class="valueClassMap['Case ID'] || 'result-value-small'">
                  N/A
                </span>
              </div>
            </div>
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

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import DetailDisplay from '~/components/DetailDisplay.vue'
import CourtCaseLink from '~/components/CourtCaseLink.vue'

const route = useRoute() // Access the route to get the ID param
const answerData = ref(null) // Store fetched court decision data
const loading = ref(true) // Track loading state

const config = useRuntimeConfig()

async function fetchAnswer(id: string) {
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
  {
    key: 'Legal Provision Articles',
    label: 'Source',
  },
  { key: 'Case ID', label: 'related cases' },
  { key: 'Related Literature', label: '' },
]

const valueClassMap = {
  Question: 'result-value-medium',
  Answer: 'result-value-large',
  'Legal provision articles': 'result-value-small',
  'Case ID': 'result-value-small',
}

// Preprocess data to handle custom rendering cases
const processedAnswerData = computed(() => {
  if (!answerData.value) return null
  //console.log(processedAnswerData)
  return {
    ...answerData.value,
    'Legal provision articles':
      answerData.value['Legal provision articles'] || '',
    'Case ID': answerData.value['Case ID']
      ? answerData.value['Case ID'].split(',').map((caseId) => caseId.trim())
      : [],
  }
})

const filteredKeyLabelPairs = computed(() => {
  if (processedAnswerData.value?.Answer === 'No data') {
    return keyLabelPairs.filter(
      (pair) => pair.key !== 'Legal provision articles'
    )
  }
  return keyLabelPairs
})

onMounted(() => {
  const id = route.params.id as string
  fetchAnswer(id).then(() => {
    if (answerData.value?.Themes) {
    }
  })
})
</script>
