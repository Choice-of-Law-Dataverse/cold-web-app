<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <div class="col-span-12">
        <DetailDisplay
          :loading="loading"
          :resultData="processedLegalInstrument"
          :keyLabelPairs="keyLabelPairs"
          :valueClassMap="valueClassMap"
          formattedSourceTable="Legislation"
          :formattedJurisdiction="formattedJurisdiction"
          :formattedTheme="formattedTheme"
        >
          <!-- Slot for Legal provisions -->
          <template #legal-provisions-ids="{ value }">
            <div>
              <div v-if="value && value.trim()">
                <LegalProvision
                  v-for="(provisionId, index) in value.split(',')"
                  :key="index"
                  :provisionId="provisionId.trim()"
                  :class="index === 0 ? 'no-margin' : ''"
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
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import DetailDisplay from '~/components/DetailDisplay.vue'
import LegalProvision from '~/components/LegalProvision.vue'

const route = useRoute() // Access the route to get the ID param
const instrument = route.params.instrument as string
const theme = route.params.theme as string

const legalInstrument = ref(null) // Store fetched court decision data
const loading = ref(true) // Track loading state

const config = useRuntimeConfig()

const formattedJurisdiction = ref([])
const formattedTheme = ref([])

watch(legalInstrument, (newValue) => {
  if (newValue) {
    formattedJurisdiction.value = [newValue['Instrument']]
    formattedTheme.value = [newValue['Theme']]
  }
})

const deslugify = (slug: string) => {
  return slug.replace(/-/g, ' ') // Convert hyphens back to spaces
}

async function fetchLegalInstrument(instrument: string, theme: string) {
  const jsonPayload = {
    table: 'Themes',
    filters: [
      {
        column: 'Instrument',
        value: deslugify(instrument),
      },
      {
        column: 'Theme',
        value: deslugify(theme),
      },
    ],
  }

  try {
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonPayload),
      }
    )

    if (!response.ok)
      throw new Error('Failed to fetch international legal instrument')

    const result = await response.json()

    if (Array.isArray(result) && result.length > 0) {
      legalInstrument.value = result[0] // Set data

      await nextTick() // Ensure Vue updates before dependent computed properties run
    } else {
      legalInstrument.value = null // Handle empty responses
    }
  } catch (error) {
    console.error('Error fetching international legal instrument:', error)
  } finally {
    loading.value = false
  }
}

// Define the keys and labels for dynamic rendering
const keyLabelPairs = computed(() => {
  // Wait until `legalInstrument` is fully available
  if (!legalInstrument.value)
    return [
      { key: 'Provision', label: 'Provision' },
      { key: 'Full text', label: 'Loading Full Text...' }, // Temporary label while data loads
    ]

  return [
    { key: 'Provision', label: 'Provision' },
    {
      key: 'Full text',
      label: `${legalInstrument.value.Instrument} Full Text`,
    },
  ]
})

const valueClassMap = {
  Abbreviation: 'result-value-medium',
  'Title (in English)': 'result-value-small',
  'Compatible with the HCCH Principles?': 'result-value-medium',
  'Publication date': 'result-value-small',
  'Entry into force': 'result-value-small',
  'Official Source (URL)': 'result-value-small',
}

// Computed property to transform the API response
const processedLegalInstrument = computed(() => {
  if (!legalInstrument.value) return null

  return {
    ...legalInstrument.value,
    Source: legalInstrument.value['Source'] || 'N/A', // Ensure a fallback if empty
  }
})

onMounted(async () => {
  fetchLegalInstrument(instrument, theme)

  await nextTick() // Ensure the DOM updates with the rendered content
})
</script>
