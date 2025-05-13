<template>
  <div>
    <span v-if="showLabel" class="label">Related Literature</span>

    <template v-if="useId">
      <ul v-if="loadingTitles">
        <li><LoadingBar class="pt-[11px]" /></li>
      </ul>
      <ul v-else-if="displayedLiteratureIds.length">
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

    <template v-else>
      <ul v-if="loading">
        <li><LoadingBar class="pt-[11px]" /></li>
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
import { ref, computed, watch, onMounted } from 'vue'
import ShowMoreLess from '../ui/ShowMoreLess.vue'
import LoadingBar from '../layout/LoadingBar.vue'

const props = defineProps({
  themes: { type: String, required: false }, // Now optional
  valueClassMap: { type: String, default: 'result-value-small' },
  literatureId: { type: String, default: '' },
  literatureTitle: { type: [Array, String], default: '' },
  useId: { type: Boolean, default: false },
  showLabel: { type: Boolean, default: true },
  emptyValueBehavior: {
    type: Object,
    default: () => ({
      action: 'display',
      fallback: 'No related literature available',
    }),
  },
})

const config = useRuntimeConfig()

const splitAndTrim = (val) =>
  Array.isArray(val)
    ? val
    : val
      ? val.split(',').map((item) => item.trim())
      : []

const literatureIds = computed(() => splitAndTrim(props.literatureId))

const fetchLiteratureTitlesById = async (ids) => {
  if (!ids.length) return []
  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/details/`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids }),
      }
    )
    if (!response.ok) throw new Error('Failed to fetch literature details')
    const data = await response.json()
    // data should be an object with keys as IDs and values as objects with Title
    return ids.map((id) => data[id]?.Title || 'Untitled')
  } catch {
    return ids.map(() => 'Untitled')
  }
}

const literatureTitles = ref([])
const loadingTitles = ref(false)

watch(
  () => props.literatureId,
  async (newIds) => {
    if (props.useId) {
      const ids = splitAndTrim(newIds)
      loadingTitles.value = true
      literatureTitles.value = []
      literatureTitles.value = await fetchLiteratureTitlesById(ids)
      loadingTitles.value = false
    }
  },
  { immediate: true }
)

const literatureList = ref([])
const loading = ref(true)
const showAll = ref(false)

const getDisplayed = (arr) =>
  !showAll.value && arr.length > 5 ? arr.slice(0, 3) : arr
const displayedLiterature = computed(() => getDisplayed(literatureList.value))
const displayedLiteratureIds = computed(() => getDisplayed(literatureIds.value))
const displayedLiteratureTitles = computed(() =>
  getDisplayed(literatureTitles.value)
)

async function fetchRelatedLiterature(themes) {
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
    literatureList.value =
      data.results && typeof data.results === 'object'
        ? Object.entries(data.results).map(([key, item]) => ({
            title: item.Title || item.title || 'Untitled',
            id: item.id || key,
          }))
        : []
  } catch {
    literatureList.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (!props.useId && props.themes) fetchRelatedLiterature(props.themes)
})
</script>
