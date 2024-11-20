<template>
  <DetailDisplay
    :loading="loading"
    :resultData="processedLegalInstrument"
    :keyLabelPairs="keyLabelPairs"
    :valueClassMap="valueClassMap"
    formattedSourceTable="Legislation"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import DetailDisplay from '~/components/DetailDisplay.vue'

const route = useRoute() // Access the route to get the ID param
const legalInstrument = ref(null) // Store fetched court decision data
const loading = ref(true) // Track loading state

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

    if (!response.ok) throw new Error('Failed to fetch legislation')

    legalInstrument.value = await response.json()
  } catch (error) {
    console.error('Error fetching legislation:', error)
  } finally {
    loading.value = false
  }
}

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Abbreviation', label: 'Name' },
  { key: 'Title (in English)', label: 'Official Title' },
  {
    key: 'Compatible with the HCCH Principles?',
    label: 'Compatible with the HCCH Principles?',
  },
  {
    key: 'Publication date',
    label: 'Publication date',
  },
  { key: 'Entry into force', label: 'Entry into force' },
  { key: 'Official Source (URL)', label: 'Official Source' },
  {
    key: 'Relevant Provisions',
    label: 'Relevant Provisions',
  },
]

const valueClassMap = {
  Abbreviation: 'result-value-medium',
  'Title (in English)': 'result-value-small',
  'Compatible with the HCCH Principles?': 'result-value-medium',
  'Publication date': 'result-value-small',
  'Entry into force': 'result-value-small',
  'Official Source (URL)': 'result-value-small',
  'Relevant Provisions': 'result-value-small',
}

// Computed property to transform the API response
const processedLegalInstrument = computed(() => {
  if (!legalInstrument.value) return null

  return {
    ...legalInstrument.value,
    'Compatible with the HCCH Principles?': legalInstrument.value[
      'Compatible with the HCCH Principles?'
    ]
      ? 'Yes'
      : 'No',
  }
})

onMounted(() => {
  const id = route.params.id as string // Get ID from the route
  fetchLegalInstrument(id)
})
</script>
