<template>
  <div>
    <p class="label mb-1">
      {{ sectionLabel }}
      <InfoTooltip v-if="sectionTooltip" :text="sectionTooltip" />
    </p>
    <span v-if="instrumentTitle !== null">
      <NuxtLink v-if="displayTitle && id" :to="generateInstrumentLink(id)">{{
        displayTitle
      }}</NuxtLink>
      <span v-else>{{ id }}</span>
    </span>
    <LoadingBar v-else />
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRuntimeConfig } from '#imports'
import { NuxtLink } from '#components'
import LoadingBar from '~/components/layout/LoadingBar.vue'
import InfoTooltip from '~/components/ui/InfoTooltip.vue'

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  section: {
    type: String,
    default: 'Amended by',
  },
  sectionLabel: {
    type: String,
    required: true,
  },
  sectionTooltip: {
    type: String,
    default: '',
  },
  table: {
    type: String,
    default: 'Domestic Instruments',
  },
})

const config = useRuntimeConfig()
const title = ref(null)
const instrumentTitle = ref(null)
const articlePart = ref('')

function parseIdParts(id) {
  // Split at first whitespace
  const match = String(id).match(/^(\S+)\s+(.+)$/)
  if (match) {
    return { instrumentId: match[1], article: match[2] }
  } else {
    return { instrumentId: id, article: '' }
  }
}

async function fetchTitle(instrumentId) {
  if (!instrumentId) return
  try {
    const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ table: props.table, id: instrumentId }),
    })
    if (!response.ok) throw new Error('Failed to fetch instrument title')
    const data = await response.json()
    instrumentTitle.value =
      data['Abbreviation'] || data['Title (in English)'] || instrumentId
  } catch (err) {
    console.error('Error fetching instrument title:', err)
    instrumentTitle.value = instrumentId
  }
}

const displayTitle = computed(() => {
  // If loading instrumentTitle, show nothing (handled by LoadingBar)
  if (instrumentTitle.value === null) return ''
  // Compose display: article part (if any), then instrument title (if any)
  let result = ''
  if (articlePart.value) {
    result += articlePart.value
  }
  if (instrumentTitle.value) {
    if (result) result += ', '
    result += instrumentTitle.value
  }
  // Fallback: if nothing, show id
  return result || props.id
})

watch(
  () => props.id,
  (newId) => {
    title.value = null
    instrumentTitle.value = null
    articlePart.value = ''
    const { instrumentId, article } = parseIdParts(newId)
    articlePart.value = article
    fetchTitle(instrumentId)
  },
  { immediate: true }
)

function generateInstrumentLink(instrumentId) {
  let base = props.table.toLowerCase().replace(/\s+/g, '-')
  if (base.endsWith('s')) {
    base = base.slice(0, -1)
  }
  // Handle whitespace after the ID: replace first whitespace after ID with #, remove all further whitespaces
  let idStr = String(instrumentId)
  // Replace the first whitespace after the ID with #
  idStr = idStr.replace(/\s+/, '#')
  // Remove all further whitespaces after the first #
  const hashIndex = idStr.indexOf('#')
  if (hashIndex !== -1) {
    const before = idStr.slice(0, hashIndex + 1)
    const after = idStr.slice(hashIndex + 1).replace(/\s+/g, '')
    idStr = before + after
  }
  return `/${base}/${idStr}`
}
</script>
