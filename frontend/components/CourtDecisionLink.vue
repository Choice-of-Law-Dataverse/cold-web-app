<template>
  <div>
    <NuxtLink v-if="title" :to="`/court-decision/${caseId}`">
      {{ title }}
    </NuxtLink>
    <span v-else>Loading...</span>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const config = useRuntimeConfig()

// Props
const props = defineProps({
  caseId: {
    type: String,
    required: true,
  },
})

// Reactive state for the case title
const title = ref(null)

// Fetch the court case title on mount
async function fetchCaseTitle() {
  const payload = {
    table: 'Court Decisions',
    id: props.caseId,
  }

  try {
    const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      console.error(`Failed to fetch case title for ID: ${props.caseId}`)
      return
    }

    const data = await response.json()
    const fetchedTitle = (data['Case Title'] || '').trim()
    // If the title is exactly "Not found", use the Case Citation instead
    title.value =
      fetchedTitle === 'Not found'
        ? (data['Case Citation'] || 'Unknown Title').trim()
        : fetchedTitle
  } catch (error) {
    console.error(`Error fetching case title for ID: ${props.caseId}`, error)
    title.value = 'Error'
  }
}

onMounted(() => {
  fetchCaseTitle()
})
</script>
