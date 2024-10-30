<template>
  <DetailDisplay
    :loading="loading"
    :resultData="courtDecision"
    :keyLabelPairs="keyLabelPairs"
    formattedSourceTable="Court Decision"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DetailDisplay from '~/components/DetailDisplay.vue'

const route = useRoute() // Access the route to get the ID param
const courtDecision = ref(null) // Store fetched court decision data
const loading = ref(true) // Track loading state

async function fetchCourtDecision(id: string) {
  const jsonPayload = {
    table: 'Court decisions',
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

    if (!response.ok) throw new Error('Failed to fetch court decision')

    courtDecision.value = await response.json()
  } catch (error) {
    console.error('Error fetching court decision:', error)
  } finally {
    loading.value = false
  }
}

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  // { key: 'Jurisdiction Names', label: 'Jurisdiction' },
  // { key: 'Themes', label: 'Themes' },
  { key: 'Case', label: 'Case Title' },
  { key: 'Abstract', label: 'Abstract' },
  {
    key: 'Relevant facts / Summary of the case',
    label: 'RELEVANT FACTS / SUMMARY OF THE CASE',
  },
  {
    key: 'Relevant rules of law involved',
    label: 'RELEVANT RULES OF LAW INVOLVED',
  },
  { key: 'Choice of law issue', label: 'choice of law issue' },
  { key: "Court's position", label: "COURT'S POSITION" },
  {
    key: 'Text of the relevant legal provisions',
    label: 'TEXT OF THE RELEVANT LEGAL PROVISIONS',
  },
]

onMounted(() => {
  const id = route.params.id as string // Get ID from the route
  fetchCourtDecision(id)
})
</script>
