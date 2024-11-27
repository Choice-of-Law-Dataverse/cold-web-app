<template>
  <div class="container">
    <div class="col-span-12">
      <DetailDisplay
        :loading="loading"
        :resultData="jurisdictionData"
        :keyLabelPairs="keyLabelPairs"
        :valueClassMap="valueClassMap"
        formattedSourceTable="Jurisdictions"
        :showHeader="false"
      />
      <!-- Only render JurisdictionComparison if jurisdictionData is loaded -->
      <JurisdictionComparison
        v-if="!loading && jurisdictionData?.Name"
        :jurisdiction="jurisdictionData.Name"
        :compareJurisdiction="compareJurisdiction"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DetailDisplay from '~/components/DetailDisplay.vue'
import JurisdictionComparison from '~/components/JurisdictionComparison.vue'

const route = useRoute() // Access the route to get the ID param
const router = useRouter()
const jurisdictionData = ref(null) // Store fetched jurisdiction data
const loading = ref(true) // Track loading state

// Extract `c` query parameter
const compareJurisdiction = ref((route.query.c as string) || null)

// Fetch the jurisdiction details
async function fetchJurisdiction(name: string) {
  const jsonPayload = {
    table: 'Jurisdictions',
    filters: [{ column: 'Name', value: name }],
  }

  try {
    const response = await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/full_table',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonPayload),
      }
    )

    if (!response.ok) throw new Error('Failed to fetch jurisdiction')

    const data = await response.json()
    // Extract the required values
    jurisdictionData.value = {
      Name: data[0]?.Name || 'N/A', // Default to 'N/A' if not found
      'Jurisdictional differentiator':
        data[0]?.['Jurisdictional differentiator'] || 'N/A',
    }
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
  const jurisdictionName = (route.params.id as string).replace(/_/g, ' ') // Convert '_' to spaces
  fetchJurisdiction(jurisdictionName)
})

// Watch for changes to the `c` query parameter and update `compareJurisdiction`
watch(
  () => route.query.c,
  (newCompare) => {
    compareJurisdiction.value = (newCompare as string) || null
  }
)
</script>
