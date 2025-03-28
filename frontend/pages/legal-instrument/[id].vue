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
                <div class="label-key pb-4 pt-4">Selected Provisions</div>
                <LegalProvision
                  v-for="(provisionId, index) in value.split(',')"
                  :key="index"
                  :provisionId="provisionId.trim()"
                  :class="index === 0 ? 'no-margin' : ''"
                  :textType="textType"
                  @update:hasEnglishTranslation="hasEnglishTranslation = $event"
                />
              </div>
              <div v-else>
                <span>N/A</span>
              </div>
            </div>
          </template>
          <template #entry-into-force="{ value }">
            <p class="result-value-small">
              {{ formatDate(value) || 'N/A' }}
            </p>
          </template>

          <template #publication-date="{ value }">
            <p class="result-value-small">
              {{ formatDate(value) || 'N/A' }}
            </p>
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
const textType = ref('Full Text of the Provision (English Translation)')
const hasEnglishTranslation = ref(false)

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
const keyLabelPairs = computed(() => {
  const apiData = legalInstrument.value || {}

  const hasPublicationDate = apiData['Publication Date'] !== undefined
  const hasEntryIntoForce = apiData['Entry Into Force'] !== undefined

  return [
    { key: 'Title (in English)', label: 'Name' },
    { key: 'Official Title', label: 'Official Title' },
    // Only include 'Date' if neither of the others exist
    !hasPublicationDate && !hasEntryIntoForce
      ? { key: 'Date', label: 'Date' }
      : null,
    hasPublicationDate
      ? { key: 'Publication Date', label: 'Publication Date' }
      : null,
    hasEntryIntoForce
      ? { key: 'Entry Into Force', label: 'Entry Into Force' }
      : null,
    { key: 'Abbreviation', label: 'Abbreviation' },
    apiData['Compatible With the HCCH Principles?']
      ? {
          key: 'Compatible With the HCCH Principles?',
          label: 'Compatible With the HCCH Principles?',
        }
      : null,
    { key: 'Source (URL)', label: 'Official Source' },
    { key: 'Domestic Legal Provisions', label: '' },
  ].filter((item) => item && apiData[item.key] !== undefined)
})

const valueClassMap = {
  Abbreviation: 'result-value-small',
  'Title (in English)': 'result-value-medium',
  'Compatible With the HCCH Principles?': 'result-value-medium',
  Date: 'result-value-small',
  'Publication Date': 'result-value-small',
  'Entry Into Force': 'result-value-small',
  'Source (URL)': 'result-value-small',
}

// Computed property to transform the API response
const processedLegalInstrument = computed(() => {
  if (!legalInstrument.value) return null

  const processed = {
    ...legalInstrument.value,
    Themes: legalInstrument.value['Themes Name'], // Map Themes name to Themes
  }

  if (legalInstrument.value['Compatible With the HCCH Principles?']) {
    processed['Compatible With the HCCH Principles?'] = 'Yes'
  }

  return processed
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
