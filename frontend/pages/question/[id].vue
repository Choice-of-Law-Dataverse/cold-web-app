<template>
  <div class="container">
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
      </DetailDisplay>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import DetailDisplay from '~/components/DetailDisplay.vue'
import CourtCaseLink from '~/components/CourtCaseLink.vue'

const route = useRoute() // Access the route to get the ID param
const answerData = ref(null) // Store fetched court decision data
const loading = ref(true) // Track loading state

async function fetchAnswer(id: string) {
  const jsonPayload = {
    table: 'Answers',
    id: id,
  }

  try {
    const response = await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/curated_search/details',
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

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Questions', label: 'Question' },
  { key: 'Answer', label: 'Answer' },
  {
    key: 'Legal provision articles',
    label: 'Source',
  },
  { key: 'Case ID', label: 'related cases' },
]

const valueClassMap = {
  Questions: 'result-value-medium',
  Answer: 'result-value-large',
  'Legal provision articles': 'result-value-medium',
  'Case ID': 'result-value-small',
}

// Preprocess data to handle custom rendering cases
const processedAnswerData = computed(() => {
  if (!answerData.value) return null

  return {
    ...answerData.value,
    'Legal provision articles':
      answerData.value['Legal provision articles'] || '',
    'Case ID': answerData.value['Case ID'] || '',
  }
})

onMounted(() => {
  const id = route.params.id as string // Get ID from the route
  fetchAnswer(id)
})
</script>
