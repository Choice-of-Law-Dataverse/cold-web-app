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
const oupChapterSource = ref(null) // Store the fetched OUP chapter source

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

// Function to fetch OUP JD Chapter source
// Function to fetch OUP JD Chapter source
async function fetchOupChapterSource() {
  if (!props.fallbackData?.['Name (from Jurisdiction)']) return

  const jsonPayload = {
    table: 'Literature',
    filters: [
      {
        column: 'Jurisdiction',
        value: props.fallbackData['Name (from Jurisdiction)'],
      },
      {
        column: 'OUP JD Chapter',
        value: true,
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

    if (!response.ok) throw new Error('Failed to fetch OUP JD Chapter source')

    const data = await response.json()
    if (data.length > 0) {
      oupChapterSource.value = { title: data[0].Title, id: data[0].ID }
    }
  } catch (error) {
    console.error('Error fetching OUP JD Chapter source:', error)
  }
}

// Compute final list of sources
const computedSources = computed(() => {
  return props.sources
    .map((source) =>
      source === props.fallbackData?.['Name (from Jurisdiction)'] &&
      oupChapterSource.value
        ? oupChapterSource.value // Replace jurisdiction name with OUP chapter link
        : source
    )
    .concat(primarySource.value) // Append primary source
    .filter(Boolean)
})

// Fetch both sources when the component mounts
onMounted(() => {
  fetchPrimarySource()
  fetchOupChapterSource()
})
</script>
