<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="modifiedCourtDecision"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    sourceTable="Court Decisions"
  >
    <template #publication-date-iso="{ value }">
      <p class="result-value-small">
        {{ formatDate(value) || 'N/A' }}
      </p>
    </template>
    <template #related-literature="{ value }">
      <RelatedLiterature
        :themes="themes"
        :valueClassMap="valueClassMap['Related Literature']"
        :useId="false"
      />
    </template>
  </BaseDetailLayout>

  <!-- Error Alert -->
  <UAlert
    v-if="error"
    type="error"
    class="mx-auto mt-4"
    style="max-width: var(--container-width)"
  >
    {{ error }}
  </UAlert>
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

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  courtDecision,
  courtDecisionConfig
)

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
    'Related Literature': themes.value,
  }
})

const fetchCourtDecision = async () => {
  try {
    await fetchData({
      table: 'Court Decisions',
      id: route.params.id,
    })
  } catch (err) {
    console.error('Failed to fetch court decision:', err)
  }
}

onMounted(() => {
  fetchCourtDecision()
})

// Refetch if the route ID changes
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      fetchCourtDecision()
    }
  }
)
</script>
