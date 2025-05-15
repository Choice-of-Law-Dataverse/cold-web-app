<template>
  <div v-if="shouldShowSection">
    <span v-if="showLabel" class="label">{{ label }}</span>

    <template v-if="useId">
      <ul v-if="loadingTitles">
        <li><LoadingBar class="pt-[11px]" /></li>
      </ul>
      <ul v-else>
        <li
          v-for="(title, index) in displayedTitles"
          :key="literatureIds[index]"
          :class="valueClassMap"
        >
          <NuxtLink :to="`/literature/${literatureIds[index]}`">
            {{ title }}
          </NuxtLink>
        </li>
        <ShowMoreLess
          v-if="literatureIds.length > 5 && !loadingTitles"
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
  label: { type: String, default: 'Related Literature' },
  themes: String,
  valueClassMap: { type: String, default: 'result-value-small' },
  literatureId: { type: String, default: '' },
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
const showAll = ref(false)
const loadingTitles = ref(false)
const loading = ref(false)
const literatureTitles = ref([])
const literatureList = ref([])

const splitAndTrim = (val) =>
  Array.isArray(val)
    ? val
    : val
      ? val.split(',').map((item) => item.trim())
      : []

const literatureIds = computed(() => splitAndTrim(props.literatureId))

const shouldShowSection = computed(
  () =>
    loadingTitles.value ||
    hasRelatedLiterature.value ||
    (!props.useId && (loading.value || literatureList.value.length)) ||
    (!hasRelatedLiterature.value &&
      props.emptyValueBehavior.action === 'display')
)

const hasRelatedLiterature = computed(() =>
  props.useId
    ? literatureTitles.value.some((title) => title && title.trim())
    : literatureList.value.length > 0
)

const displayedTitles = computed(() => {
  const arr = literatureTitles.value
  return !showAll.value && arr.length > 5 ? arr.slice(0, 3) : arr
})

const displayedLiterature = computed(() => {
  const arr = literatureList.value
  return !showAll.value && arr.length > 5 ? arr.slice(0, 3) : arr
})

async function fetchLiteratureTitlesById(ids) {
  if (!ids.length) return []
  loadingTitles.value = true
  const titles = await Promise.all(
    ids.map(async (id) => {
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
        if (!response.ok) throw new Error('Error fetching title')
        const data = await response.json()
        return data?.Title ? data.Title : data[id]?.Title || ''
      } catch {
        return ''
      }
    })
  )
  literatureTitles.value = titles
  loadingTitles.value = false
}

watch(
  () => props.literatureId,
  (newIds) => {
    if (props.useId) fetchLiteratureTitlesById(splitAndTrim(newIds))
  },
  { immediate: true }
)

async function fetchRelatedLiterature(themes) {
  if (!themes) return
  loading.value = true
  try {
    const response = await fetch(`${config.public.apiBaseUrl}/search/`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        filters: [
          { column: 'tables', values: ['Literature'] },
          { column: 'themes', values: themes.split(',').map((t) => t.trim()) },
        ],
      }),
    })
    if (!response.ok) throw new Error('Failed to fetch related literature')
    const data = await response.json()
    literatureList.value = Array.isArray(data.results)
      ? data.results.map((item) => ({
          title: item.Title || item.title || 'Untitled',
          id: item.id,
        }))
      : []
  } catch {
    literatureList.value = []
  } finally {
    loading.value = false
  }
}

watch(
  () => props.themes,
  (themes) => {
    if (!props.useId && themes) fetchRelatedLiterature(themes)
  },
  { immediate: true }
)

onMounted(() => {
  if (!props.useId && props.themes) fetchRelatedLiterature(props.themes)
})
</script>
