<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="modifiedCourtDecision"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Court Decisions"
  >
    <template #related-literature="{ value }">
      <RelatedLiterature
        :themes="themes"
        :valueClassMap="valueClassMap['Related Literature']"
        :useId="false"
      />
    </template>
  </BaseDetailLayout>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'
import { courtDecisionConfig } from '~/config/pageConfigs'

const route = useRoute()
const { loading, error, data: courtDecision, fetchData } = useApiFetch()

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(courtDecision, courtDecisionConfig)

// Debug the court decision data
watch(courtDecision, (newValue) => {
  console.log('Court Decision Data:', newValue)
  if (newValue) {
    console.log('Themes:', newValue['Themes'])
  }
})

const themes = computed(() => {
  if (!courtDecision.value) return ''
  const themesData = courtDecision.value['Themes']
  console.log('Processing themes for RelatedLiterature:', themesData)
  return themesData || ''
})

const modifiedCourtDecision = computed(() => {
  if (!courtDecision.value) return null
  return {
    ...courtDecision.value,
    'Case Title':
      courtDecision.value['Case Title'] === 'Not found'
        ? courtDecision.value['Case Citation']
        : courtDecision.value['Case Title'],
    'Related Literature': themes.value
  }
})

onMounted(() => {
  fetchData({
    table: 'Court Decisions',
    id: route.params.id,
  })
})
</script>
