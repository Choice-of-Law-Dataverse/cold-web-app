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
          :formattedJurisdiction="formattedJurisdiction"
          :formattedTheme="formattedTheme"
        >
          <template #full-text="{ value }">
            <div class="grid grid-cols-2 gap-8">
              <!-- Left Column: Original Full Text -->
              <div>
                <p class="label-key -mb-1">
                  {{ legalInstrument?.Instrument }} Full Text
                </p>
                <p class="text-sm leading-relaxed">
                  {{ legalInstrument?.['Full Text'] || 'N/A' }}
                </p>
              </div>

              <!-- Right Column: Select Instrument + Comparison Full Text -->
              <div>
                <!-- Move USelectMenu to the top -->
                <div class="ml-[-10px] mt-[9px] mb-[-9px]">
                  <USelectMenu
                    placeholder="Select International Instrument"
                    v-model="selectedInstrument"
                    variant="none"
                    :options="availableInstruments"
                    @update:model-value="onSelectInstrument"
                    :ui="{
                      placeholder: 'text-[var(--color-cold-purple)] mb-[11px]',
                    }"
                    :popper="{ offsetDistance: -15, placement: 'bottom-start' }"
                    :uiMenu="{
                      select: 'label',
                      width: 'min-w-[200px] max-w-[200px]',
                    }"
                  />
                </div>

                <!-- Placeholder text when no instrument is selected -->
                <div
                  v-if="!secondaryInstrument"
                  class="text-sm text-gray-400 mt-2"
                >
                  {{ processedLegalInstrument?.['Comparison Full Text'] }}
                </div>

                <!-- Comparison Full Text -->
                <div v-if="secondaryInstrument">
                  <p class="text-sm leading-relaxed">
                    {{ secondaryInstrument?.['Full Text'] || 'N/A' }}

                    <!-- Link to the selected legal instrument -->
                    <UButton
                      class="link-button"
                      variant="link"
                      icon="i-material-symbols:arrow-forward"
                      trailing
                      :to="`/international-legal-instrument/${slugify(selectedInstrument)}/${encodeURIComponent(theme)}`"
                    >
                      Go to Legal Instrument
                    </UButton>
                  </p>
                </div>
              </div>
            </div>
          </template>

          <template #source v-if="processedLegalInstrument?.Source">
            <UButton
              class="link-button mt-[-24px] mb-4"
              variant="link"
              icon="i-material-symbols:open-in-new"
              trailing
              :to="processedLegalInstrument.Source"
              v-if="processedLegalInstrument?.Source"
              target="_blank"
            >
              View Source
            </UButton>
            <span v-else>No source available</span>
          </template>

          <!-- Related Literature -->
          <template #related-literature>
            <RelatedLiterature
              :themes="processedLegalInstrument['Title of the Provision'] || ''"
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

const legalInstrument = ref(null) // Store fetched data
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
    formattedTheme.value = [newValue['Title of the Provision']]
  }
  console.log('newValue: ', newValue)
})

const slugify = (str) => {
  return str
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/[^\w-]/g, '') // Remove non-word characters except hyphens
}

const deslugify = (slug: string) => {
  return slug.replace(/-/g, ' ') // Convert hyphens back to spaces
}

async function fetchLegalInstrument(instrument: string, theme: string) {
  const jsonPayload = {
    table: 'International Legal Provisions',
    filters: [
      {
        column: 'Instrument',
        value: deslugify(instrument),
      },
      {
        column: 'Title of the Provision',
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
    table: 'International Legal Provisions',
    filters: [
      { column: 'Title of the Provision', value: deslugify(themeParam) },
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
    table: 'International Legal Provisions',
    filters: [
      {
        column: 'Instrument',
        value: deslugify(instrumentParam),
      },
      {
        column: 'Title of the Provision',
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

async function fetchSourceURL(instrumentName) {
  const jsonPayload = {
    table: 'International Instruments',
    filters: [{ column: 'Name', value: instrumentName }],
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

    if (!response.ok) throw new Error('Failed to fetch source URL')

    const result = await response.json()

    if (Array.isArray(result) && result.length > 0) {
      return result[0].URL ?? null // Extract URL if available
    }
  } catch (error) {
    console.error('Error fetching source URL:', error)
  }

  return null // Default if nothing is found
}

// Define the keys and labels for dynamic rendering
const keyLabelPairs = computed(() => {
  if (!legalInstrument.value)
    return [
      { key: 'Provision', label: 'Provision' },
      { key: 'Full Text', label: '' },
    ]

  const pairs = [
    { key: 'Provision', label: 'Provision' },
    { key: 'Full Text', label: '' },
  ]

  // Only include the Source field if a valid URL exists
  if (legalInstrument.value.Source) {
    pairs.push({ key: 'Source', label: '' })
  }

  pairs.push(
    { key: 'Related Question', label: 'Related Question' },
    { key: 'Related Literature', label: '' }
  )

  return pairs
})

const valueClassMap = {
  // Abbreviation: 'result-value-medium',
}

// Computed property to transform the API response
const processedLegalInstrument = computed(() => {
  if (!legalInstrument.value) return null

  return {
    ...legalInstrument.value,
    Source: legalInstrument.value.Source,
    'Related Question': '[In development]',
    'Select International Instrument': '',
    // ✅ Remove the fallback text from "Comparison Full Text"
    'Comparison Full Text': secondaryInstrument.value
      ? secondaryInstrument.value['Full Text']
      : 'Compare with another International Legal Instrument', // ✅ Empty string instead of duplicate text
  }
})

onMounted(async () => {
  await fetchLegalInstrument(instrument, theme)
  await fetchInstrumentsForTheme(theme)
  if (legalInstrument.value) {
    legalInstrument.value.Source = await fetchSourceURL(
      legalInstrument.value.Instrument
    )
  }
  await nextTick() // Ensure the DOM updates with the rendered content
})
</script>

<style scoped>
.custom-select .u-select-trigger {
  text-transform: uppercase;
}
</style>
