<template>
  <DetailDisplay
    :loading="loading"
    :resultData="jurisdictionData"
    :keyLabelPairs="keyLabelPairs"
    :valueClassMap="valueClassMap"
    formattedSourceTable="Jurisdictions"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DetailDisplay from '~/components/DetailDisplay.vue'

const route = useRoute() // Access the route to get the ID param
const jurisdictionData = ref(null) // Store fetched jurisdiction data
const loading = ref(true) // Track loading state

// Fetch the jurisdiction details
async function fetchJurisdiction(id: string) {
  const jsonPayload = {
    table: 'Jurisdictions',
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

    if (!response.ok) throw new Error('Failed to fetch jurisdiction')

    jurisdictionData.value = await response.json()
  } catch (error) {
    console.error('Error fetching jurisdiction:', error)
  } finally {
    loading.value = false
  }
}

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Name', label: 'Jurisdiction' },
  {
    key: 'Jurisdictional differentiator',
    label: 'Jurisdictional differentiator',
  },
]

const valueClassMap = {
  Name: 'result-value-medium',
  'Jurisdictional differentiator': 'result-value-small',
}

// Fetch jurisdiction data on component mount
onMounted(() => {
  const id = route.params.id as string // Get ID from the route
  fetchJurisdiction(id)
})
</script>
