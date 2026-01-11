<template>
  <BaseLegalRenderer
    :items="value"
    :valueClassMap="valueClassMap"
    :emptyValueBehavior="emptyValueBehavior"
    defaultClass="result-value-small"
  >
    <template #default="{ item }">
      <NuxtLink :to="generateCourtDecisionLink(item)">
        <template v-if="caseTitles[item] !== undefined">
          {{ caseTitles[item] }}
        </template>
        <template v-else>
          <LoadingBar />
        </template>
      </NuxtLink>
    </template>
  </BaseLegalRenderer>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRuntimeConfig } from '#imports'
import BaseLegalRenderer from './BaseLegalRenderer.vue'
import { NuxtLink } from '#components'
import LoadingBar from '@/components/layout/LoadingBar.vue'

const props = defineProps({
  value: {
    type: [Array, String],
    default: () => [],
  },
  valueClassMap: {
    type: String,
    default: '',
  },
})

const config = useRuntimeConfig()
const caseTitles = ref({})

// Fetch the title of a court decision given its ID.
async function fetchCaseTitle(caseId) {
  if (!caseId || caseTitles.value[caseId]) return
  const jsonPayload = { table: 'Court Decisions', id: caseId }
  try {
    const response = await fetch(`/api/proxy/search/details`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jsonPayload),
    })
    if (!response.ok) throw new Error('Failed to fetch case title')
    const data = await response.json()
    // If 'Case Title' is not available or equals "NA", use 'Case Citation'
    const title = data['Case Title']
    const finalTitle =
      title && title !== 'NA' ? title : data['Case Citation'] || caseId
    caseTitles.value[caseId] = finalTitle
  } catch (err) {
    console.error('Error fetching case title:', err)
    caseTitles.value[caseId] = caseId
  }
}

// Watch the items and fetch titles for each case ID.
watch(
  () => props.value,
  (newValue) => {
    const items = Array.isArray(newValue) ? newValue : [newValue]
    const uniqueIds = new Set(items)
    uniqueIds.forEach((id) => {
      fetchCaseTitle(id)
    })
  },
  { immediate: true }
)

// Helper to generate the link URL for a court decision.
function generateCourtDecisionLink(caseId) {
  return `/court-decision/${caseId}`
}
</script>
