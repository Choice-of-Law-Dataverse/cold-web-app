<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedArbitralAward"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    :formattedJurisdiction="formattedJurisdictions"
    :formattedTheme="formattedThemes"
    :showSuggestEdit="true"
    sourceTable="Arbitral Award"
  />
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import { useApiFetch } from '@/composables/useApiFetch'
import { useDetailDisplay } from '@/composables/useDetailDisplay'
import { arbitralAwardConfig } from '@/config/pageConfigs'
import { useHead } from '#imports'

const route = useRoute()
const router = useRouter()

const { loading, error, data: arbitralAward, fetchData } = useApiFetch()

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  arbitralAward,
  arbitralAwardConfig
)

const processedArbitralAward = computed(() => {
  if (!arbitralAward.value) return null
  const raw = arbitralAward.value
  const derivedTitle =
    raw['Award Title'] || raw['Case Title'] || raw['Title'] || raw['Name']
  return {
    ...raw,
    Title: derivedTitle,
    // Flatten potential nested institutions like in rules
    'Arbitral Institution': Array.isArray(raw?.related_arbitral_institutions)
      ? raw.related_arbitral_institutions
          .map((inst) => inst?.Institution)
          .filter((v) => v && String(v).trim())
          .join(', ')
      : undefined,
  }
})

// Jurisdictions for header labels
const formattedJurisdictions = computed(() => {
  const list = arbitralAward.value?.related_jurisdictions
  if (!Array.isArray(list)) return []
  const names = list
    .map((j) => j?.Name)
    .filter((n) => n && String(n).trim())
    .map((n) => String(n).trim())
  return [...new Set(names)]
})

// Themes for header labels
const formattedThemes = computed(() => {
  const list = arbitralAward.value?.related_themes
  if (!Array.isArray(list)) return []
  const themes = list
    .map((t) => t?.Theme)
    .filter((n) => n && String(n).trim())
    .map((n) => String(n).trim())
  return [...new Set(themes)]
})

// Dynamic page title based on Title
watch(
  processedArbitralAward,
  (newVal) => {
    if (!newVal) return
    const title = newVal['Case Number']
    const pageTitle =
      title && String(title).trim()
        ? `Arbitral Award Case Number ${title} — CoLD`
        : 'Arbitral Award — CoLD'
    useHead({
      title: pageTitle,
      link: [
        { rel: 'canonical', href: `https://cold.global${route.fullPath}` },
      ],
      meta: [{ name: 'description', content: pageTitle }],
    })
  },
  { immediate: true }
)

onMounted(async () => {
  try {
    await fetchData({ table: 'Arbitral Awards', id: route.params.id })
  } catch (err) {
    if (err.isNotFound) {
      router.push({
        path: '/error',
        query: { message: 'Arbitral award not found' },
      })
    } else {
      console.error('Error fetching arbitral award:', err)
    }
  }
})
</script>

<style scoped></style>
