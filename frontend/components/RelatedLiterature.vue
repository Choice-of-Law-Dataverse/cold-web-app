<template>
  <div>
    <span class="label">Related Literature</span>

    <ul v-if="loading">
      <li class="text-gray-500">Loading...</li>
    </ul>

    <ul v-else-if="literatureList.length">
      <li
        v-for="(item, index) in literatureList"
        :key="index"
        :class="valueClassMap"
      >
        <NuxtLink :to="`/literature/${item.id}`">
          {{ item.title }}
        </NuxtLink>
      </li>
    </ul>

    <p v-else :class="valueClassMap">No related literature available</p>
  </div>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue'

const config = useRuntimeConfig()

// Props: themes for search
const props = defineProps({
  themes: {
    type: String,
    required: true,
  },
  valueClassMap: {
    type: String,
    default: 'result-value-small',
  },
})

// Reactive variables
const literatureList = ref<{ id: string; title: string }[]>([])
const loading = ref(true)

// Function to fetch related literature
async function fetchRelatedLiterature(themes: string) {
  if (!themes) return

  const jsonPayload = {
    filters: [
      { column: 'tables', values: ['Literature'] },
      { column: 'themes', values: themes.split(',').map((t) => t.trim()) },
    ],
  }

  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/full_text_search`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonPayload),
      }
    )

    if (!response.ok) throw new Error('Failed to fetch related literature')

    const data = await response.json()
    literatureList.value = Object.values(data.results).map((item: any) => ({
      title: item.Title,
      id: item.id,
    }))
  } catch (error) {
    console.error('Error fetching related literature:', error)
  } finally {
    loading.value = false
  }
}

// Fetch data when themes change
watchEffect(() => {
  fetchRelatedLiterature(props.themes)
})
</script>
