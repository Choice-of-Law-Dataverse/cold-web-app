<template>
  <div v-if="shouldShowSection" class="mt-12">
    <span v-if="showLabel" class="label flex flex-row items-center">
      {{ label }}
      <InfoPopover v-if="tooltip" :text="tooltip" />
    </span>
    <ul v-if="loadingTitles || loading">
      <LoadingBar class="ml-[-22px] pt-[11px]" />
    </ul>
    <ul v-else-if="displayedLiterature.length">
      <li
        v-for="item in displayedLiterature"
        :key="item.id"
        :class="valueClassMap"
      >
        <NuxtLink :to="`/literature/L-${item.id}`">
          {{ item.title }}
        </NuxtLink>
      </li>
      <ShowMoreLess
        v-if="fullLiteratureList.length > 5"
        v-model:is-expanded="showAll"
        label="related literature"
      />
    </ul>
    <p
      v-else-if="emptyValueBehavior.action === 'display'"
      :class="valueClassMap"
    >
      {{ emptyValueBehavior.fallback }}
    </p>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import ShowMoreLess from '@/components/ui/ShowMoreLess.vue'
import LoadingBar from '@/components/layout/LoadingBar.vue'
import InfoPopover from '~/components/ui/InfoPopover.vue'

import { useApiClient } from '@/composables/useApiClient'

const props = defineProps({
  label: { type: String, default: 'Related Literature' },
  tooltip: { type: String, default: '' },
  themes: { type: String, default: '' },
  valueClassMap: { type: String, default: 'result-value-small' },
  literatureId: { type: String, default: '' },
  useId: { type: Boolean, default: false }, // deprecated, kept for backward compatibility
  mode: { type: String, default: 'themes' }, // 'id' | 'themes' | 'both'
  showLabel: { type: Boolean, default: true },
  emptyValueBehavior: {
    type: Object,
    default: () => ({
      action: 'display',
      fallback: 'No related literature available',
    }),
  },
})

const showAll = ref(false)
const loadingTitles = ref(false)
const loading = ref(false)
const literatureTitles = ref([])
const literatureList = ref([])
const mergedLiterature = ref([])

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
    loading.value ||
    hasRelatedLiterature.value ||
    (!hasRelatedLiterature.value &&
      props.emptyValueBehavior.action === 'display')
)

const hasRelatedLiterature = computed(() => {
  if (props.mode === 'id') {
    return literatureTitles.value.some((title) => title && title.trim())
  } else if (props.mode === 'themes') {
    return literatureList.value.length > 0
  } else if (props.mode === 'both') {
    return mergedLiterature.value.length > 0
  }
  return false
})

const fullLiteratureList = computed(() => {
  if (props.mode === 'id') {
    return literatureTitles.value.map((title, i) => ({
      id: literatureIds.value[i],
      title,
    }))
  } else if (props.mode === 'themes') {
    return literatureList.value
  } else if (props.mode === 'both') {
    return mergedLiterature.value
  }
  return []
})

const displayedLiterature = computed(() => {
  const arr = fullLiteratureList.value
  return !showAll.value && arr.length > 5 ? arr.slice(0, 3) : arr
})
const { apiClient } = useApiClient()

async function fetchLiteratureTitlesById(ids, useJurisdictionsColumn = false) {
  if (!ids.length) return []
  loadingTitles.value = true
  const titles = await Promise.all(
    ids.map(async (id) => {
      try {
        const data = await apiClient('/search/details', {
          body: {
            table: 'Literature',
            id,
            column: useJurisdictionsColumn
              ? 'Jurisdictions Literature ID'
              : undefined,
          },
        })
        return data?.Title ? data.Title : data[id]?.Title || ''
      } catch {
        return ''
      }
    })
  )
  literatureTitles.value = titles
  loadingTitles.value = false
}

async function fetchRelatedLiterature(themes) {
  if (!themes) return
  loading.value = true
  try {
    const data = await apiClient('/search/', {
      body: {
        filters: [
          { column: 'tables', values: ['Literature'] },
          { column: 'themes', values: themes.split(',').map((t) => t.trim()) },
        ],
        page_size: 100,
      },
    })
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

async function fetchBoth() {
  // Fetch by ID (using Jurisdictions Literature ID column)
  const ids = literatureIds.value
  await fetchLiteratureTitlesById(ids, true)
  // Fetch by themes
  await fetchRelatedLiterature(props.themes)
  // Merge and deduplicate by id
  const idSet = new Set()
  const merged = []
  // Add ID-based first
  ids.forEach((id, i) => {
    if (id && literatureTitles.value[i] && !idSet.has(id)) {
      merged.push({ id, title: literatureTitles.value[i] })
      idSet.add(id)
    }
  })
  // Add theme-based, skipping duplicates
  literatureList.value.forEach((item) => {
    if (item.id && !idSet.has(item.id)) {
      merged.push(item)
      idSet.add(item.id)
    }
  })
  mergedLiterature.value = merged
}

watch(
  () => [props.literatureId, props.themes, props.mode],
  async ([newIds, newThemes, newMode]) => {
    if (newMode === 'id') {
      await fetchLiteratureTitlesById(splitAndTrim(newIds))
    } else if (newMode === 'themes') {
      if (newThemes) await fetchRelatedLiterature(newThemes)
    } else if (newMode === 'both') {
      await fetchBoth()
    }
  },
  { immediate: true }
)

onMounted(() => {
  if (props.mode === 'id') {
    fetchLiteratureTitlesById(literatureIds.value)
  } else if (props.mode === 'themes') {
    if (props.themes) fetchRelatedLiterature(props.themes)
  } else if (props.mode === 'both') {
    fetchBoth()
  }
})
</script>
