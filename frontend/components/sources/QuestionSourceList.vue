<template>
  <div>
    <ul class="result-value-small">
      <!-- Domestic Legal Provision bullet point -->
      <template v-if="fallbackData['Domestic Legal Provisions']">
        <li
          v-for="(provision, index) in fallbackData[
            'Domestic Legal Provisions'
          ].split(',')"
          :key="'domestic-legal-' + index"
        >
          <LegalProvisionRenderer
            :value="provision"
            :fallbackData="fallbackData"
          />
        </li>
      </template>
      <template v-else-if="fallbackData['Domestic Instruments ID']">
        <li
          v-for="(instrument, index) in fallbackData[
            'Domestic Instruments ID'
          ].split(',')"
          :key="'domestic-instrument-' + index"
        >
          <LegalProvisionRenderer
            skipArticle
            :value="instrument"
            :fallbackData="fallbackData"
          />
        </li>
      </template>
      <!-- Updated OUP Chapter bullet point -->
      <template v-if="fallbackData['Jurisdictions Literature ID']">
        <template v-if="literatureTitles.length">
          <li v-for="(item, index) in literatureTitles" :key="index">
            <a :href="`/literature/${item.id}`">{{ item.title }}</a>
          </li>
        </template>
        <li v-else><LoadingBar class="pt-[9px]" /></li>
      </template>
      <template v-else>
        <li>
          <template v-if="oupChapterSource">
            <a :href="`/literature/${oupChapterSource.id}`">{{
              oupChapterSource.title
            }}</a>
          </template>
          <template v-else> OUP Chapter </template>
        </li>
      </template>
      <!-- <li>Primary Literature</li> -->
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import LegalProvisionRenderer from '../legal/LegalProvisionRenderer.vue'
import LoadingBar from '../layout/LoadingBar.vue'

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

// NEW: Fetch literature titles logic for 'Jurisdictions Literature ID'
const literatureTitles = ref([])
async function fetchLiteratureTitles(idStr) {
  const ids = idStr.split(',').map((id) => id.trim())
  const promises = ids.map(async (id) => {
    try {
      const response = await fetch(
        `${config.public.apiBaseUrl}/search/details`,
        {
          method: 'POST',
          headers: {
            authorization: `Bearer ${config.public.FASTAPI}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ table: 'Literature', id }),
        }
      )
      if (!response.ok) throw new Error('Failed to fetch literature title')
      const data = await response.json()
      return { id, title: data['Title'] }
    } catch (err) {
      console.error('Error fetching literature title:', err)
      return { id, title: id }
    }
  })
  literatureTitles.value = await Promise.all(promises)
}
if (props.fallbackData && props.fallbackData['Jurisdictions Literature ID']) {
  fetchLiteratureTitles(props.fallbackData['Jurisdictions Literature ID'])
}
</script>
