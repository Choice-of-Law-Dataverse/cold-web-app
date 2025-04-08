<template>
  <div>
    <!-- Render legal provisions inline with fetched title -->
    <template v-for="(prov, index) in processedProvisions" :key="index">
      <NuxtLink :to="generateLegalProvisionLink(prov.raw)">
        {{ instrumentTitles[prov.instrumentId] || prov.instrumentId }}
        {{ prov.articleId }}
      </NuxtLink>
      <span v-if="index !== processedProvisions.length - 1">, </span>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import {
  generateLegalProvisionLink,
  parseLegalProvisionLink,
} from '~/utils/legal'
import { useRuntimeConfig } from '#imports'

const props = defineProps({
  value: {
    type: String,
    default: '',
  },
  fallbackData: {
    type: Object,
    required: true,
  },
  valueClassMap: {
    type: Object,
    default: () => ({}),
  },
})

// Compute provision items from props (unchanged logic)
const provisionItems = computed(() => {
  if (props.value && props.value.trim()) {
    return props.value.split(',')
  }
  if (
    props.fallbackData['Legislation-ID'] &&
    props.fallbackData['Legislation-ID'].trim()
  ) {
    return props.fallbackData['Legislation-ID'].split(',')
  }
  if (
    props.fallbackData['More information'] &&
    props.fallbackData['More information'].trim()
  ) {
    return [props.fallbackData['More information'].replace(/\n/g, ' ').trim()]
  }
  return []
})

// Parse each provision into instrumentId and articleId using parseLegalProvisionLink
const processedProvisions = computed(() =>
  provisionItems.value.map((item) => {
    const { instrumentId, articleId } = parseLegalProvisionLink(item)
    return { raw: item.trim(), instrumentId, articleId }
  })
)

const config = useRuntimeConfig()
const instrumentTitles = ref({})

async function fetchInstrumentTitle(instrumentId) {
  if (!instrumentId || instrumentTitles.value[instrumentId]) return
  const jsonPayload = { table: 'Domestic Instruments', id: instrumentId }
  try {
    const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jsonPayload),
    })
    if (!response.ok) throw new Error('Failed to fetch instrument title')
    const data = await response.json()
    instrumentTitles.value[instrumentId] =
      data['Title (in English)'] || instrumentId
  } catch (err) {
    console.error('Error fetching instrument title:', err)
    instrumentTitles.value[instrumentId] = instrumentId
  }
}

// Watch processed provisions and fetch missing instrument titles
watch(
  processedProvisions,
  (newProvisions) => {
    const uniqueIds = new Set(newProvisions.map((p) => p.instrumentId))
    uniqueIds.forEach((id) => {
      if (!instrumentTitles.value[id]) {
        fetchInstrumentTitle(id)
      }
    })
  },
  { immediate: true }
)
</script>
