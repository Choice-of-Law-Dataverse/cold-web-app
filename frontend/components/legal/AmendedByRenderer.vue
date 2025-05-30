<template>
  <span v-if="title !== null">
    <NuxtLink v-if="title && id" :to="generateInstrumentLink(id)">{{
      title
    }}</NuxtLink>
    <span v-else>{{ id }}</span>
  </span>
  <LoadingBar v-else />
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRuntimeConfig } from '#imports'
import { NuxtLink } from '#components'
import LoadingBar from '../layout/LoadingBar.vue'

const props = defineProps({
  id: {
    type: String,
    required: true,
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
      body: JSON.stringify({ table: 'Domestic Instruments', id: instrumentId }),
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
  return `/domestic-instrument/${instrumentId}`
}
</script>
