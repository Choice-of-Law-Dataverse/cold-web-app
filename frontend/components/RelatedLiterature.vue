<template>
  <div>
    <span class="label">Related Literature</span>

    <ul v-if="loading">
      <li class="text-gray-500">Loading...</li>
    </ul>

    <ul v-else-if="literatureList.length">
      <li
        v-for="(item, index) in displayedLiterature"
        :key="index"
        :class="valueClassMap"
      >
        <NuxtLink :to="`/literature/${item.id}`">
          {{ item.title }}
        </NuxtLink>
      </li>
    </ul>

    <!-- Show more button only if the list has more than 5 items and we haven't expanded -->
    <button
      v-if="literatureList.length > 5 && !showAll"
      @click="showAll = true"
      class="mt-2 text-blue-500 underline"
    >
      Show more ({{ totalMatches }} total)
    </button>

    <!-- Show less button when expanded -->
    <button
      v-if="literatureList.length > 5 && showAll"
      @click="showAll = false"
      class="mt-2 text-blue-500 underline"
    >
      Show less
    </button>

    <p v-if="!literatureList.length && !loading" :class="valueClassMap">
      No related literature available
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watchEffect } from 'vue'

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
const totalMatches = ref(0)
const loading = ref(true)
const showAll = ref(false)

// Computed property: Show nothing initially if the list is longer than 5
const displayedLiterature = computed(() => {
  if (!showAll.value) {
    return literatureList.value.length > 5
      ? literatureList.value.slice(0, 3)
      : literatureList.value
  }
  return literatureList.value
})

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
    const response = await fetch(`${config.public.apiBaseUrl}/search/`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jsonPayload),
    })

    if (!response.ok) throw new Error('Failed to fetch related literature')

    const data = await response.json()
    literatureList.value = Object.values(data.results).map((item: any) => ({
      title: item.Title,
      id: item.id,
    }))
    totalMatches.value = data.total_matches // Store total matches count
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
