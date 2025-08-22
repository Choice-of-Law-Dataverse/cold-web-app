<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedArbitralRule"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Arbitral Rule"
  />
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '@/components/layouts/BaseDetailLayout.vue'
import { useApiFetch } from '@/composables/useApiFetch'
import { useDetailDisplay } from '@/composables/useDetailDisplay'
import { arbitralRuleConfig } from '@/config/pageConfigs'
import { useHead } from '#imports'

const route = useRoute()
const router = useRouter()

const { loading, error, data: arbitralRule, fetchData } = useApiFetch()

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  arbitralRule,
  arbitralRuleConfig
)

const processedArbitralRule = computed(() => {
  if (!arbitralRule.value) return null
  return {
    ...arbitralRule.value,
  }
})

// Dynamic page title based on Set_of_Rules
watch(
  arbitralRule,
  (newVal) => {
    if (!newVal) return
    const title = newVal['Set_of_Rules']
    const pageTitle =
      title && String(title).trim() ? `${title} — CoLD` : 'Arbitral Rule — CoLD'
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
    await fetchData({ table: 'Arbitral Rules', id: route.params.id })
  } catch (err) {
    if (err.isNotFound) {
      router.push({
        path: '/error',
        query: { message: 'Arbitral rule not found' },
      })
    } else {
      console.error('Error fetching arbitral rule:', err)
    }
  }
})
</script>

<style scoped></style>
