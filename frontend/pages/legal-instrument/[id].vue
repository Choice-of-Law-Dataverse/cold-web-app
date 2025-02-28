<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <DetailDisplay
          :loading="loading"
          :resultData="processedLegalInstrument"
          :keyLabelPairs="keyLabelPairs"
          :valueClassMap="valueClassMap"
          formattedSourceTable="Legal Instrument"
        >
          <!-- Slot for Legal provisions -->
          <template #domestic-legal-provisions="{ value }">
            <div>
              <div v-if="value && value.trim()">
                <USelectMenu
                  v-model="textType"
                  :options="[
                    'Full Text of the Provision (Original Language)',
                    'Full Text of the Provision (English Translation)',
                  ]"
                  class="mb-4"
                />
                <div class="label-key pb-4 pt-4">Selected Provisions</div>
                <LegalProvision
                  v-for="(provisionId, index) in value.split(',')"
                  :key="index"
                  :provisionId="provisionId.trim()"
                  :class="index === 0 ? 'no-margin' : ''"
                  :textType="textType"
                />
              </div>
              <div v-else>
                <span>N/A</span>
              </div>
            </div>
          </template>
        </DetailDisplay>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import DetailDisplay from '~/components/DetailDisplay.vue'
import LegalProvision from '~/components/LegalProvision.vue'

const route = useRoute() // Access the route to get the ID param
const legalInstrument = ref(null) // Store fetched court decision data
const loading = ref(true) // Track loading state
const textType = ref('Full Text of the Provision (Original Language)')

const config = useRuntimeConfig()

async function fetchLegalInstrument(id: string) {
  const jsonPayload = {
    table: 'Domestic Instruments',
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

    if (!response.ok) throw new Error('Failed to fetch legislation')

    legalInstrument.value = await response.json()
  } catch (error) {
    console.error('Error fetching legislation:', error)
  } finally {
    loading.value = false
  }
}

// Define the keys and labels for dynamic rendering
const keyLabelPairs = [
  { key: 'Abbreviation', label: 'Name' },
  { key: 'Title (in English)', label: 'Official Title' },
  {
    key: 'Compatible with the HCCH Principles?',
    label: 'Compatible with the HCCH Principles?',
  },
  {
    key: 'Publication Date',
    label: 'Publication Date',
  },
  { key: 'Entry Into Force', label: 'Entry Into Force' },
  { key: 'Source (URL)', label: 'Official Source' },
  {
    key: 'Domestic Legal Provisions',
    label: '',
  },
]

const valueClassMap = {
  Abbreviation: 'result-value-medium',
  'Title (in English)': 'result-value-small',
  'Compatible with the HCCH Principles?': 'result-value-medium',
  'Publication Date': 'result-value-small',
  'Entry Into Force': 'result-value-small',
  'Source (URL)': 'result-value-small',
}

// Computed property to transform the API response
const processedLegalInstrument = computed(() => {
  if (!legalInstrument.value) return null

  return {
    ...legalInstrument.value,
    'Compatible with the HCCH Principles?': legalInstrument.value[
      'Compatible with the HCCH Principles?'
    ]
      ? 'Yes'
      : 'No',
    Themes: legalInstrument.value['Themes Name'], // Map Themes name to Themes
  }
})

onMounted(async () => {
  const id = route.params.id as string // Get ID from the route
  await fetchLegalInstrument(id) // Wait for the legal instrument data to load

  await nextTick() // Ensure the DOM updates with the rendered content

  // Check if the URL contains a hash and scroll to the corresponding element
  const anchor = document.querySelector(window.location.hash)
  if (anchor) {
    anchor.scrollIntoView({ behavior: 'smooth' }) // Smoothly scroll to the element
  }
})
</script>
