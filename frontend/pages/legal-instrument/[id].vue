<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute() // Access the route to get the ID param
const legalInstrument = ref(null) // Store fetched court decision data
const loading = ref(true) // Track loading state
const errorMessage = ref('') // To store an error message if it exists

async function fetchLegalInstrument(id: string) {
  const jsonPayload = {
    table: 'Legislation',
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

    const data = await response.json()

    // Check if the response contains an error
    if (data.error) {
      errorMessage.value = data.error // Store the error message
      legalInstrument.value = null // Clear court decision data
    } else {
      legalInstrument.value = data // Store actual data
      errorMessage.value = '' // Clear any previous error
    }
  } catch (error) {
    errorMessage.value = 'An unexpected error occurred'
    console.error('Error fetching court decision:', error)
  } finally {
    loading.value = false
  }
}

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Jurisdiction Names', label: 'Jurisdiction' },
  { key: 'Themes', label: 'Themes' },
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
  fetchLegalInstrument(id)
})
</script>

<template>
  <BackButton />
  <div v-if="loading">Loading...</div>
  <div v-else>
    <h1>Legal Instrument Details</h1>
    <p v-if="errorMessage">{{ errorMessage }}</p>
    <div v-else>
      <h1>Legal Instrument Details</h1>

      <!-- Loop over the keyLabelPairs array to display each key-value pair dynamically -->
      <div v-for="(item, index) in keyLabelPairs" :key="index">
        <p class="result-key">{{ item.label }}</p>
        <p class="result-value">
          {{ legalInstrument?.[item.key] || 'N/A' }}
        </p>
        <!-- Insert hardcoded label after "Jurisdiction Names" -->
        <p v-if="item.key === 'Jurisdiction Names'"></p>
        <p class="result-key">Label</p>
        <p class="result-value">Court Decision</p>
      </div>
    </div>
  </div>
</template>
