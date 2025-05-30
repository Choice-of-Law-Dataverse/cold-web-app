<template>
  <div>
    <p class="label mb-1">
      {{ sectionLabel }}
      <InfoTooltip v-if="sectionTooltip" :text="sectionTooltip" />
    </p>
    <span v-if="title !== null">
      <NuxtLink v-if="title && id" :to="generateInstrumentLink(id)">{{
        title
      }}</NuxtLink>
      <span v-else>{{ id }}</span>
    </span>
    <LoadingBar v-else />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRuntimeConfig } from '#imports'
import { NuxtLink } from '#components'
import LoadingBar from '../layout/LoadingBar.vue'
import InfoTooltip from '../ui/InfoTooltip.vue'

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
    title.value = data['Title (in English)'] || instrumentId
  } catch (err) {
    console.error('Error fetching instrument title:', err)
    title.value = instrumentId
  }
}

watch(
  () => props.id,
  (newId) => {
    title.value = null
    fetchTitle(newId)
  },
  { immediate: true }
)

function generateInstrumentLink(instrumentId) {
  let base = props.table.toLowerCase().replace(/\s+/g, '-')
  if (base.endsWith('s')) {
    base = base.slice(0, -1)
  }
  return `/${base}/${instrumentId}`
}
</script>
