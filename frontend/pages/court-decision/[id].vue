<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <DetailDisplay
          v-if="courtDecision"
          :resultData="modifiedCourtDecision"
          :keyLabelPairs="computedKeyLabelPairs"
          :valueClassMap="valueClassMap"
          formattedSourceTable="Court Decisions"
        >
          <template #related-literature>
            <RelatedLiterature
              :themes="courtDecision?.Themes || ''"
              :valueClassMap="valueClassMap['Related Literature']"
            />
          </template>
        </DetailDisplay>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import DetailDisplay from '~/components/DetailDisplay.vue'

const route = useRoute() // Access the route to get the ID param
const config = useRuntimeConfig()

const id = route.params.id as string

// Fetch court decision using useAsyncData (SSR-compatible)
const {
  data: courtDecision,
  pending: loading,
  error,
} = useAsyncData(`court-decision-${id}`, async () => {
  const jsonPayload = {
    table: 'Court Decisions',
    id: id,
  }

  const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
    method: 'POST',
    headers: {
      authorization: `Bearer ${config.public.FASTAPI}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(jsonPayload),
  })

  if (!response.ok) throw new Error('Failed to fetch court decision')

  return await response.json()
})

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Case Title', label: 'Case Title' },
  { key: 'Date (GPT-o3-mini)', label: 'Date' },
  { key: 'Abstract', label: 'Abstract' },
  { key: 'Relevant Facts', label: 'Relevant Facts' },
  { key: 'Choice of Law Issue', label: 'Choice of Law Issue' },
  { key: "Court's Position", label: "Court's Position" },
  {
    key: 'Text of the Relevant Legal Provisions',
    label: 'Text of the Relevant Legal Provisions',
  },
  { key: 'Case Citation', label: 'Case Citation' },
  { key: 'Related Literature', label: '' },
]

const computedKeyLabelPairs = computed(() => {
  const data: Record<string, any> = courtDecision.value || {}

  return keyLabelPairs.map((pair) => ({
    ...pair,
    value:
      pair.key === 'Case Title' && data['Case Title'] === 'Not found'
        ? data['Case Citation']
        : data[pair.key],
  }))
})

const modifiedCourtDecision = computed(() => {
  const data: Record<string, any> = courtDecision.value || {}
  return {
    ...data,
    'Case Title':
      data['Case Title'] === 'Not found'
        ? data['Case Citation']
        : data['Case Title'],
  }
})

const valueClassMap = {
  'Case Title': 'result-value-medium',
  Abstract: 'result-value-small',
  'Relevant Facts': 'result-value-small',
  'Choice of Law Issue': 'result-value-small',
  "Court's Position": 'result-value-small',
  'Text of the Relevant Legal Provisions': 'result-value-small',
}
</script>
