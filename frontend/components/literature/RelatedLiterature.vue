<template>
  <div>
    <span v-if="showLabel" class="label">Related Literature</span>

    <!-- If we're using literature ID mode -->
    <template v-if="useId">
      <ul v-if="displayedLiteratureIds.length">
        <li
          v-for="(id, index) in displayedLiteratureIds"
          :key="id"
          :class="valueClassMap"
        >
          <NuxtLink :to="`/literature/${id}`">
            {{ displayedLiteratureTitles[index] }}
          </NuxtLink>
        </li>
        <ShowMoreLess
          v-if="literatureIds.length > 5"
          v-model:isExpanded="showAll"
          label="related literature"
        />
      </ul>
      <p
        v-else-if="emptyValueBehavior.action === 'display'"
        :class="valueClassMap"
      >
        {{ emptyValueBehavior.fallback }}
      </p>
    </template>

    <!-- Else, use the normal themes-based display -->
    <template v-else>
      <ul v-if="loading">
        <li><LoadingBar class="pt-[9px]" /></li>
      </ul>

      <ul v-else-if="literatureList.length">
        <li
          v-for="item in displayedLiterature"
          :key="item.id"
          :class="valueClassMap"
        >
          <NuxtLink :to="`/literature/${item.id}`">
            {{ item.title }}
          </NuxtLink>
        </li>
        <ShowMoreLess
          v-if="literatureList.length > 5"
          v-model:isExpanded="showAll"
          label="related literature"
        />
      </ul>

      <p
        v-else-if="emptyValueBehavior.action === 'display'"
        :class="valueClassMap"
      >
        {{ emptyValueBehavior.fallback }}
      </p>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watchEffect, watch, onMounted } from 'vue'
import ShowMoreLess from '../ui/ShowMoreLess.vue'
import LoadingBar from '../layout/LoadingBar.vue'

const props = defineProps({
  themes: {
    type: String,
    required: true,
  },
  valueClassMap: {
    type: String,
    default: 'result-value-small',
  },
  literatureId: {
    type: String,
    default: '',
  },
  literatureTitle: {
    type: [Array, String],
    default: '',
  },
  useId: {
    type: Boolean,
    default: false,
  },
  showLabel: {
    type: Boolean,
    default: true,
  },
  emptyValueBehavior: {
    type: Object,
    default: () => ({
      action: 'display',
      fallback: 'No related literature available',
    }),
  },
})

const config = useRuntimeConfig()

// Split the literatureId string into an array
const literatureIds = computed(() => {
  return props.literatureId
    ? props.literatureId.split(',').map((item) => item.trim())
    : []
})

// Similarly, if the API returns multiple literature titles, split them too.
const literatureTitles = computed(() => {
  return Array.isArray(props.literatureTitle)
    ? props.literatureTitle
    : props.literatureTitle
      ? [props.literatureTitle]
      : []
})

// Reactive variables
const literatureList = ref([])
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

const displayedLiteratureIds = computed(() => {
  if (!showAll.value && literatureIds.value.length > 5) {
    return literatureIds.value.slice(0, 3)
  }
  return literatureIds.value
})

const displayedLiteratureTitles = computed(() => {
  if (!showAll.value && literatureTitles.value.length > 5) {
    return literatureTitles.value.slice(0, 3)
  }
  return literatureTitles.value
})

// Function to fetch related literature
async function fetchRelatedLiterature(themes) {
  if (!themes) {
    console.log('No themes provided')
    return
  }

  console.log('Fetching related literature for themes:', themes)

  const jsonPayload = {
    filters: [
      { column: 'tables', values: ['Literature'] },
      { column: 'themes', values: themes.split(',').map((t) => t.trim()) },
    ],
  }

  console.log('API request payload:', jsonPayload)

  try {
    const response = await fetch(`${config.public.apiBaseUrl}/search/`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jsonPayload),
    })

    if (!response.ok) {
      console.error(
        'API response not OK:',
        response.status,
        response.statusText
      )
      throw new Error('Failed to fetch related literature')
    }

    const data = await response.json()
    console.log('API response:', data)

    // Check if we have results and they're in the expected format
    if (!data.results || typeof data.results !== 'object') {
      console.log('No results found or unexpected response format')
      literatureList.value = []
      return
    }

    // Map the results to the expected format
    literatureList.value = Object.entries(data.results).map(([key, item]) => {
      console.log('Processing item:', { key, item })
      return {
        title: item.Title || item.title || 'Untitled',
        id: item.id || key, // Use the item's id if available, otherwise use the key
      }
    })

    console.log('Processed literature list:', literatureList.value)
  } catch (error) {
    console.error('Error fetching related literature:', error)
    literatureList.value = []
  } finally {
    loading.value = false
  }
}

// Debug the themes prop
watch(
  () => props.themes,
  (newThemes) => {
    console.log('Themes prop changed:', newThemes)
    if (!props.useId) {
      console.log('Fetching related literature due to themes change')
      fetchRelatedLiterature(newThemes)
    }
  },
  { immediate: true }
)

// Initial fetch
onMounted(() => {
  console.log('Component mounted, themes:', props.themes)
  if (!props.useId) {
    console.log('Fetching related literature on mount')
    fetchRelatedLiterature(props.themes)
  }
})
</script>
