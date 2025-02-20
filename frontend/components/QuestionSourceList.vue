<template>
  <ul>
    <li
      v-for="(source, index) in computedSources"
      :key="index"
      :class="valueClass"
    >
      <template v-if="noLinkList.includes(source)">
        <span>{{ source }}</span>
      </template>
      <template v-else-if="typeof source === 'object' && source.id">
        <NuxtLink :to="`/literature/${source.id}`">
          {{ source.title }}
        </NuxtLink>
      </template>
      <template v-else>
        <LegalProvisionRenderer
          :value="source"
          :fallbackData="fallbackData"
          :valueClassMap="valueClassMap"
        />
      </template>
    </li>
  </ul>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  sources: Array,
  fallbackData: Object,
  valueClassMap: Object,
  valueClass: {
    type: String,
    default: 'result-value-small',
  },
  noLinkList: {
    type: Array,
    default: () => [],
  },
})

const config = useRuntimeConfig()
const primarySource = ref(null) // Store the fetched primary source title

// Function to fetch the primary source from API
async function fetchPrimarySource() {
  if (!props.fallbackData?.['Name (from Jurisdiction)']) return

  const jsonPayload = {
    table: 'Literature',
    filters: [
      {
        column: 'Jurisdiction',
        value: props.fallbackData['Name (from Jurisdiction)'],
      },
    ],
  }

  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonPayload),
      }
    )

    if (!response.ok) throw new Error('Failed to fetch primary source')

    const data = await response.json()
    if (data.length > 0) {
      primarySource.value = { title: data[0].Title, id: data[0].ID }
    }
  } catch (error) {
    console.error('Error fetching primary source:', error)
  }
}

// Compute final list of sources, adding the fetched primary source
const computedSources = computed(() => {
  return [...props.sources, primarySource.value].filter(Boolean)
})

// Fetch the primary source when the component mounts
onMounted(() => {
  fetchPrimarySource()
})
</script>
