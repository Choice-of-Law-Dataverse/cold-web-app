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
  fetchOupChapter: {
    type: Boolean,
    default: false, // Only fetch if explicitly requested
  },
  fetchPrimarySource: {
    type: Boolean,
    default: false, // Only fetch if explicitly requested
  },
})

const config = useRuntimeConfig()
const primarySource = ref(null) // Store the fetched primary source title
const oupChapterSource = ref(null) // Store the fetched OUP chapter source

// Function to fetch the primary source from API
async function fetchPrimarySource() {
  if (!props.fallbackData?.['Name']) return

  const jsonPayload = {
    table: 'Literature',
    filters: [
      {
        column: 'Jurisdiction',
        value: props.fallbackData['Name'],
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

    // Filter out entries where "OUP JD Chapter" is explicitly true
    const nonOupEntries = data.filter(
      (entry) => entry['OUP JD Chapter'] === null
    )

    // Select the first valid non-OUP entry as the primary source
    if (nonOupEntries.length > 0) {
      primarySource.value = nonOupEntries.map((entry) => ({
        title: entry.Title,
        id: entry.ID,
      }))
    }
  } catch (error) {
    console.error('Error fetching primary source:', error)
  }
}

// Fetch OUP JD Chapter only if the prop is true
async function fetchOupChapterSource() {
  if (!props.fetchOupChapter || !props.fallbackData?.['Name']) return

  const jsonPayload = {
    table: 'Literature',
    filters: [
      {
        column: 'Jurisdiction',
        value: props.fallbackData['Name'],
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
  return [
    ...props.sources,
    props.fetchOupChapter ? oupChapterSource.value : null,
    ...(props.fetchPrimarySource && Array.isArray(primarySource.value)
      ? primarySource.value
      : []),
  ].filter(Boolean)
})

// Fetch both sources when the component mounts
onMounted(() => {
  if (props.fetchOupChapter) fetchOupChapterSource()
  if (props.fetchPrimarySource) fetchPrimarySource()
})
</script>
