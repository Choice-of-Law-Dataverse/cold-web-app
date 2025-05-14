<template>
  <div v-if="loadingTitles || hasRelatedLiterature">
    <span class="label">Related Literature</span>

    <template v-if="useId">
      <ul v-if="loadingTitles">
        <li><LoadingBar class="pt-[11px]" /></li>
      </ul>
      <ul>
        <li
          v-for="(title, index) in !showAll && literatureTitles.length > 5
            ? literatureTitles.slice(0, 3)
            : literatureTitles"
          :key="literatureIds[index]"
          :class="valueClassMap"
        >
          <NuxtLink :to="`/literature/${literatureIds[index]}`">
            {{ title }}
          </NuxtLink>
        </li>
        <ShowMoreLess
          v-if="literatureIds.length > 5 && loadingTitles == false"
          v-model:isExpanded="showAll"
          label="related literature"
        />
      </ul>
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
  themes: { type: String, required: false },
  valueClassMap: { type: String, default: 'result-value-small' },
  literatureId: { type: String, default: '' },
  literatureTitle: { type: [Array, String], default: '' },
  useId: { type: Boolean, default: false },
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

const literatureTitles = ref([])
const loadingTitles = ref(false)

const hasRelatedLiterature = computed(() =>
  literatureTitles.value.some((title) => title && title.trim())
)

const fetchLiteratureTitlesById = async (ids) => {
  if (!ids.length) return []
  const titles = []
  for (const id of ids) {
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
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Error response from /search/details:', errorText)
        titles.push('')
        continue
      }
      const data = await response.json()
      const title = data?.Title ? data.Title : data[id]?.Title || ''
      titles.push(
        title && typeof title === 'string' && title.trim() ? title : ''
      )
    } catch (e) {
      titles.push('')
    }
  }
  return titles
}

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
