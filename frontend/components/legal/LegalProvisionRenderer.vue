<template>
  <template v-for="(prov, index) in processedProvisions" :key="index">
    <template v-if="renderAsLi">
      <li>
        <NuxtLink :to="generateLegalProvisionLink(prov.raw)">
          <template v-if="instrumentTitles[prov.instrumentId]">
            <template v-if="!skipArticle">
              {{ formatArticle(prov.articleId) }},
              {{ instrumentTitles[prov.instrumentId] }}
            </template>
            <template v-else>
              {{ instrumentTitles[prov.instrumentId] }}
            </template>
          </template>
          <template v-else>
            <LoadingBar class="pt-[9px]" />
          </template>
        </NuxtLink>
      </li>
    </template>
    <template v-else>
      <NuxtLink :to="generateLegalProvisionLink(prov.raw)">
        <template v-if="instrumentTitles[prov.instrumentId]">
          <template v-if="!skipArticle">
            {{ formatArticle(prov.articleId) }},
            {{ instrumentTitles[prov.instrumentId] }}
          </template>
          <template v-else>
            {{ instrumentTitles[prov.instrumentId] }}
          </template>
        </template>
        <template v-else>
          <LoadingBar class="pt-[9px]" />
        </template>
      </NuxtLink>
    </template>
  </template>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import {
  generateLegalProvisionLink,
  parseLegalProvisionLink,
} from '~/utils/legal'
import { useRuntimeConfig } from '#imports'
import LoadingBar from '~/components/layout/LoadingBar.vue'

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
  // New prop to control article display
  skipArticle: {
    type: Boolean,
    default: false,
  },
  // New prop to control whether to render with <li> wrapper
  renderAsLi: {
    type: Boolean,
    default: false,
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
    const title =
      data['Abbreviation'] || data['Title (in English)'] || instrumentId
    instrumentTitles.value[instrumentId] = title
  } catch (err) {
    console.error('Error fetching instrument title:', err)
    instrumentTitles.value[instrumentId] = instrumentId
  }
}

const formatArticle = (article) =>
  article ? article.replace(/(Art\.)(\d+)/, '$1 $2') : ''

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

<style scoped>
/* Only apply bullet styling when renderAsLi is true */
li {
  list-style-type: disc; /* Forces bullet points */
  margin-left: 20px; /* Ensures proper indentation */
}
</style>
