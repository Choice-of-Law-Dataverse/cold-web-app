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
          <template #select-international-instrument="{ value }">
            <div>
              <label>Select an Instrument:</label>
              <select v-model="selectedInstrument" @change="onSelectInstrument">
                <option value="">--Choose an Instrument--</option>
                <option
                  v-for="inst in availableInstruments"
                  :key="inst"
                  :value="inst"
                >
                  {{ inst }}
                </option>
              </select>
            </div>
          </template>

          <!-- Related Literature -->
          <template #related-literature>
            <RelatedLiterature
              :themes="processedLegalInstrument?.Theme || ''"
              :valueClassMap="valueClassMap['Related Literature']"
            />
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

const route = useRoute() // Access the route to get the ID param
const instrument = route.params.instrument as string
const theme = route.params.theme as string

const legalInstrument = ref(null) // Store fetched court decision data
const loading = ref(true) // Track loading state

const config = useRuntimeConfig()

const formattedJurisdiction = ref([])
const formattedTheme = ref([])

const availableInstruments = ref<string[]>([])
const secondaryInstrument = ref(null) // Stores data for the selected instrument
const selectedInstrument = ref('')

function onSelectInstrument() {
  if (selectedInstrument.value) {
    fetchSecondaryInstrument(selectedInstrument.value) // only fetch the second instrument
  }
}

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

async function fetchInstrumentsForTheme(themeParam: string) {
  const jsonPayload = {
    table: 'Themes',
    filters: [{ column: 'Theme', value: deslugify(themeParam) }],
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
    if (!response.ok) throw new Error('Failed to fetch instruments')

    const result = await response.json()
    if (Array.isArray(result)) {
      // Extract the Instrument column
      const allInstruments = result.map((row: any) => row.Instrument)
      // Remove duplicates
      availableInstruments.value = [...new Set(allInstruments)]
    } else {
      availableInstruments.value = []
    }
  } catch (error) {
    console.error('Error fetching instruments:', error)
  }
}

async function fetchSecondaryInstrument(instrumentParam: string) {
  const jsonPayload = {
    table: 'Themes',
    filters: [
      {
        column: 'Instrument',
        value: deslugify(instrumentParam),
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

    if (!response.ok) throw new Error('Failed to fetch second instrument')

    const result = await response.json()
    console.log('Secondary fetch result:', result)

    if (Array.isArray(result) && result.length > 0) {
      secondaryInstrument.value = result[0] // Store the second instrument data
    } else {
      secondaryInstrument.value = null
    }
  } catch (error) {
    console.error('Error fetching second instrument:', error)
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
    {
      key: 'Select International Instrument',
      label: 'Select International Instrument',
    },

    { key: 'Comparison Full Text', label: 'Comparison Full Text' },
    { key: 'Source', label: 'Source' },
    { key: 'Source', label: 'Related Question' }, // 'Source' is a placeholder
    { key: 'Related Literature', label: '' },
  ]
})

const valueClassMap = {
  // Abbreviation: 'result-value-medium',
}

// Computed property to transform the API response
const processedLegalInstrument = computed(() => {
  if (!legalInstrument.value) return null

  return {
    ...legalInstrument.value,
    Source: '[In development]', //legalInstrument.value['Record ID'], // This is a placeholder
    'Related Question': '[In development]', // This is a placeholder
    'Select International Instrument':
      'Compare with another International Legal Instrument',
    // Add the second instrument’s text
    'Comparison Full Text': secondaryInstrument.value
      ? secondaryInstrument.value['Full text'] // or the correct column name
      : '', // or some fallback
  }
})

onMounted(async () => {
  await fetchLegalInstrument(instrument, theme)
  await fetchInstrumentsForTheme(theme)
  await nextTick() // Ensure the DOM updates with the rendered content
})
</script>
