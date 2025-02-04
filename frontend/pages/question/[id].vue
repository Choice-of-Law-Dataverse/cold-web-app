<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <DetailDisplay
          :loading="loading"
          :resultData="processedAnswerData"
          :keyLabelPairs="keyLabelPairs"
          :valueClassMap="valueClassMap"
          formattedSourceTable="Question"
        >
          <!-- Custom rendering for Legal provision articles -->
          <template #legal-provision-articles="{ value }">
            <LegalProvisionRenderer
              :value="value"
              :fallbackData="processedAnswerData"
              :valueClassMap="valueClassMap"
            />
          </template>

          <!-- Custom rendering for Case ID -->
          <template #case-id="{ value }">
            <div>
              <div v-if="value && value.trim()">
                <!-- Render links if value exists -->
                <CourtCaseLink
                  v-for="(caseId, index) in value.split(',')"
                  :key="index"
                  :caseId="caseId.trim()"
                  :class="valueClassMap['Case ID'] || 'result-value'"
                />
              </div>
              <div v-else>
                <!-- Render N/A if no case IDs are available -->
                <span>N/A</span>
              </div>
            </div>
          </template>
          <!-- Placeholder for Related Literature -->
          <template #related-literature="{ value }">
            <div>
              <ul v-if="Array.isArray(value) && value.length">
                <li
                  v-for="(title, index) in value"
                  :key="index"
                  :class="
                    valueClassMap['Related Literature'] || 'result-value-small'
                  "
                >
                  {{ title }}
                </li>
              </ul>
              <div v-else>
                <span
                  :class="
                    valueClassMap['Related Literature'] || 'result-value-small'
                  "
                >
                  N/A
                </span>
              </div>
            </div>
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
const relatedLiterature = ref([]) // Store related literature titles

const config = useRuntimeConfig()

async function fetchAnswer(id: string) {
  const jsonPayload = {
    table: 'Answers',
    id: id,
  }

  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/curated_search/details`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonPayload),
      }
    )

    if (!response.ok) throw new Error('Failed to fetch answer')

    answerData.value = await response.json()
  } catch (error) {
    console.error('Error fetching answer:', error)
  } finally {
    loading.value = false
  }
}

async function fetchRelatedLiterature(themes: string) {
  if (!themes) return

  const jsonPayload = {
    filters: [
      { column: 'tables', values: ['Literature'] },
      { column: 'themes', values: themes.split(', ').map((t) => t.trim()) },
    ],
  }

  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/full_text_search`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonPayload),
      }
    )

    if (!response.ok) throw new Error('Failed to fetch related literature')

    const data = await response.json()
    relatedLiterature.value = Object.values(data.results).map(
      (item: any) => item.Title
    )
  } catch (error) {
    console.error('Error fetching related literature:', error)
  }
}

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Questions', label: 'Question' },
  { key: 'Answer', label: 'Answer' },
  {
    key: 'Legal provision articles',
    label: 'Source',
  },
  { key: 'Case ID', label: 'related cases' },
  { key: 'Related Literature', label: 'Related Literature' },
]

const valueClassMap = {
  Questions: 'result-value-medium',
  Answer: 'result-value-large',
  'Legal provision articles': 'result-value-medium',
  'Case ID': 'result-value-small',
  'Related Literature': 'result-value-small',
}

// Preprocess data to handle custom rendering cases
const processedAnswerData = computed(() => {
  if (!answerData.value) return null

  return {
    ...answerData.value,
    'Legal provision articles':
      answerData.value['Legal provision articles'] || '',
    'Case ID': answerData.value['Case ID'] || '',
    'Related Literature': relatedLiterature.value.length
      ? relatedLiterature.value
      : [],
  }
})

onMounted(() => {
  const id = route.params.id as string
  fetchAnswer(id).then(() => {
    if (answerData.value?.Themes) {
      fetchRelatedLiterature(answerData.value.Themes)
    }
  })
})
</script>
