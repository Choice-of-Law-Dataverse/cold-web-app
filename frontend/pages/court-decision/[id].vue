<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <DetailDisplay
          :loading="loading"
          :resultData="courtDecision"
          :keyLabelPairs="keyLabelPairs"
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
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DetailDisplay from '~/components/DetailDisplay.vue'

const route = useRoute() // Access the route to get the ID param
const courtDecision = ref(null) // Store fetched court decision data
const loading = ref(true) // Track loading state

const config = useRuntimeConfig()

async function fetchCourtDecision(id: string) {
  const jsonPayload = {
    table: 'Court Decisions',
    id: id,
  }

  try {
    const response = await fetch(`${config.public.apiBaseUrl}/search/details`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${config.public.FASTAPI}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jsonPayload),
    })

    if (!response.ok) throw new Error('Failed to fetch court decision')

    courtDecision.value = await response.json()
  } catch (error) {
    console.error('Error fetching court decision:', error)
  } finally {
    loading.value = false
  }
}

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Case Title', label: 'Case Title' },
  { key: 'Abstract', label: 'Abstract' },
  {
    key: 'Relevant Facts',
    label: 'Relevant Facts',
  },
  // {
  //   key: 'Relevant rules of law involved',
  //   label: 'Relevant Rules of Law Involved',
  // },
  { key: 'Choice of Law Issue', label: 'Choice of Law Issue' },
  { key: "Court's Position", label: "Court's Position" },
  {
    key: 'Text of the Relevant Legal Provisions',
    label: 'Text of the Relevant Legal Provisions',
  },
  { key: 'Related Literature', label: '' },
]

const valueClassMap = {
  'Case Title': 'result-value-medium',
  Abstract: 'result-value-small',
  'Relevant Facts': 'result-value-small',
  //'Relevant rules of law involved': 'result-value-small',
  'Choice of Law Issue': 'result-value-small',
  "Court's Position": 'result-value-small',
  'Text of the Relevant Legal Provisions': 'result-value-small',
}

onMounted(() => {
  const id = route.params.id as string // Get ID from the route
  fetchCourtDecision(id)
})
</script>
