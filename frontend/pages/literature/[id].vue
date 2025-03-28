<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <DetailDisplay
          :loading="loading"
          :resultData="literature"
          :keyLabelPairs="keyLabelPairs"
          :valueClassMap="valueClassMap"
          formattedSourceTable="Literature"
        />
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DetailDisplay from '~/components/ui/BaseDetailDisplay.vue'

const route = useRoute() // Access the route to get the ID param
const literature = ref(null) // Store fetched data
const loading = ref(true) // Track loading state

const config = useRuntimeConfig()

async function fetchLiterature(id) {
  const jsonPayload = {
    table: 'Literature',
    id: id,
  }

  try {
    const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jsonPayload),
    })

    if (!response.ok) throw new Error('Failed to fetch literature')

    literature.value = await response.json()
  } catch (error) {
    console.error('Error fetching literature:', error)
  } finally {
    loading.value = false
  }
}

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Title', label: 'Title' },
  { key: 'Author', label: 'Author' },
  { key: 'Editor', label: 'Editor' },
  { key: 'Publication Year', label: 'Year' },
  { key: 'Publication Title', label: 'Publication' },
]

const valueClassMap = {
  Title: 'result-value-medium',
  Author: 'result-value-small',
  'Publication Year': 'result-value-small',
  'Publication Title': 'result-value-small',
}

onMounted(() => {
  const id = route.params.id // Get ID from the route
  fetchLiterature(id)
})
</script>
