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
        class="!mt-2"
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
import { useRoute, useRouter } from 'vue-router'
import BaseDetailLayout from '~/components/layouts/BaseDetailLayout.vue'
import RelatedLiterature from '~/components/literature/RelatedLiterature.vue'
import { useApiFetch } from '~/composables/useApiFetch'
import { useDetailDisplay } from '~/composables/useDetailDisplay'
import { courtDecisionConfig } from '~/config/pageConfigs'
import { formatDate } from '~/utils/format.js'

const route = useRoute()
const router = useRouter()
const { loading, error, data: courtDecision, fetchData } = useApiFetch()

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  courtDecision,
  courtDecisionConfig
)

// Debug the court decision data and configuration
watch(courtDecision, (newValue) => {
  if (newValue) {
  }
})

const themes = computed(() => {
  if (!courtDecision.value) return ''
  const themesData = courtDecision.value['Themes']
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
    'Case Citation': courtDecision.value['Case Citation'],
    'Publication Date ISO': formatDate(
      courtDecision.value['Publication Date ISO']
    ),
  }
})

const fetchCourtDecision = async () => {
  try {
    await fetchData({
      table: 'Court Decisions',
      id: route.params.id,
    })
  } catch (err) {
    if (err.isNotFound) {
      router.push({
        path: '/error',
        query: { message: `Court decision not found` },
      })
    } else {
      console.error('Failed to fetch court decision:', err)
    }
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
