<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

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

onMounted(() => {
  const id = route.params.id as string // Get ID from the route
  fetchCourtDecision(id)
})
</script>

<template>
  <div v-if="loading">Loading...</div>
  <div v-else>
    <h1>Court Decision Details</h1>

    <p>
      <strong>Jurisdiction Names:</strong>
      {{ courtDecision?.['Jurisdiction Names'] || 'N/A' }}
    </p>

    <p><strong>Label: </strong>Court Decision</p>

    <p>
      <strong>Themes:</strong>
      {{ courtDecision?.['Themes'] || 'N/A' }}
    </p>

    <p>
      <strong>Case Title:</strong>
      {{ courtDecision?.['Case'] || 'N/A' }}
    </p>

    <p>
      <strong>Abstract:</strong>
      {{ courtDecision?.['Abstract'] || 'N/A' }}
    </p>

    <p>
      <strong>RELEVANT FACTS / SUMMARY OF THE CASE:</strong>
      {{ courtDecision?.['Relevant facts / Summary of the case'] || 'N/A' }}
    </p>

    <p>
      <strong>RELEVANT RULES OF LAW INVOLVED:</strong>
      {{ courtDecision?.['Relevant rules of law involved'] || 'N/A' }}
    </p>

    <p>
      <strong>choice of law issue:</strong>
      {{ courtDecision?.['Choice of law issue'] || 'N/A' }}
    </p>

    <p>
      <strong>COURT'S POSITION:</strong>
      {{ courtDecision?.["Court's position"] || 'N/A' }}
    </p>

    <p>
      <strong>TEXT OF THE RELEVANT LEGAL PROVISIONS:</strong>
      {{ courtDecision?.['Text of the relevant legal provisions'] || 'N/A' }}
    </p>
  </div>
</template>
