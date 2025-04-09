<template>
  <div>
    <ul>
      <!-- Domestic Legal Provision bullet point -->
      <template v-if="fallbackData['Domestic Legal Provisions']">
        <li>
          <LegalProvisionRenderer
            :value="fallbackData['Domestic Legal Provisions']"
            :fallbackData="fallbackData"
          />
        </li>
      </template>
      <template v-else-if="fallbackData['Domestic Instruments ID']">
        <li>
          <LegalProvisionRenderer
            skipArticle
            :value="fallbackData['Domestic Instruments ID']"
            :fallbackData="fallbackData"
          />
        </li>
      </template>
      <li>OUP Chapter</li>
      <li>Primary Literature</li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import LegalProvisionRenderer from '../legal/LegalProvisionRenderer.vue'

const props = defineProps({
  sources: {
    type: Array,
    required: true,
  },
  fallbackData: {
    type: Object,
    required: true,
  },
  valueClassMap: {
    type: Object,
    required: true,
  },
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
    default: false,
  },
  fetchPrimarySource: {
    type: Boolean,
    default: false,
  },
})

const config = useRuntimeConfig()
const primarySource = ref(null)
const oupChapterSource = ref(null)
const loading = ref(false)
const error = ref(null)

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
  } catch (err) {
    console.error('Error fetching primary source:', err)
    error.value = err.message
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
  } catch (err) {
    console.error('Error fetching OUP JD Chapter source:', err)
    error.value = err.message
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
