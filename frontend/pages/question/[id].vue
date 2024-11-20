<template>
  <DetailDisplay
    :loading="loading"
    :resultData="answerData"
    :keyLabelPairs="keyLabelPairs"
    :valueClassMap="valueClassMap"
    formattedSourceTable="Question"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DetailDisplay from '~/components/DetailDisplay.vue'

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
  { key: 'Case titles', label: 'related cases' },
]

const valueClassMap = {
  Questions: 'result-value-medium',
  Answer: 'result-value-large',
  'Relevant provisions': 'result-value-medium',
}

onMounted(() => {
  const id = route.params.id as string // Get ID from the route
  fetchAnswer(id)
})
</script>
