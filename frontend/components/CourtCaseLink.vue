<template>
  <div>
    <NuxtLink v-if="title" :to="`/court-decision/${caseId}`">
      {{ title }}
    </NuxtLink>
    <span v-else>Loading...</span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Props
const props = defineProps({
  caseId: {
    type: String,
    required: true,
  },
})

// Reactive state for the case title
const title = ref<string | null>(null)

// Fetch the court case title on mount
async function fetchCaseTitle() {
  const payload = {
    table: 'Court decisions',
    id: props.caseId,
  }

  try {
    const response = await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/curated_search/details',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }
    )

    if (!response.ok) {
      console.error(`Failed to fetch case title for ID: ${props.caseId}`)
      return
    }

    const data = await response.json()
    title.value = data.Case || 'Unknown Title' // Fallback if the title is missing
  } catch (error) {
    console.error(`Error fetching case title for ID: ${props.caseId}`, error)
    title.value = 'Error'
  }
}

onMounted(() => {
  fetchCaseTitle()
})
</script>
