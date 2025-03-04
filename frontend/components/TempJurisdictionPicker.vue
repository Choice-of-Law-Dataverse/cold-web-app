<template>
  <UCard class="cold-ucard">
    <div
      class="popular-searches-container flex flex-col md:flex-row gap-6 md:items-center"
    >
      <h2 class="popular-title">Individual Jurisdiction</h2>
      <div class="suggestions w-full md:w-auto">
        <JurisdictionSelectMenu
          :countries="countries"
          @countrySelected="navigateToCountry"
        />
      </div>
    </div>
  </UCard>
</template>

<script setup>
// Imports
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import JurisdictionSelectMenu from './JurisdictionSelectMenu.vue'
import { useRuntimeConfig } from '#app' // Import Nuxt's runtime config

// Reactive states
const countries = ref([])
const router = useRouter()
const config = useRuntimeConfig()

// Fetch jurisdictions from the text file
async function fetchJurisdictions() {
  try {
    const jsonPayloads = [
      { table: 'Jurisdictions', filters: [] },
      { table: 'International Instruments', filters: [] },
    ]

    // Fetch both tables concurrently
    const responses = await Promise.all(
      jsonPayloads.map((payload) =>
        fetch(`${config.public.apiBaseUrl}/search/full_table`, {
          method: 'POST',
          headers: {
            authorization: `Bearer ${config.public.FASTAPI}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        })
      )
    )

    // Process both responses
    const [jurisdictionsData, instrumentsData] = await Promise.all(
      responses.map((res) =>
        res.ok ? res.json() : Promise.reject('Failed to load data')
      )
    )

    // Filter jurisdictions (only applies to "Jurisdictions" table)
    const relevantJurisdictions = jurisdictionsData.filter(
      (entry) => entry['Irrelevant?'] === null
    )

    // Extract "Name" field
    const jurisdictionNames = relevantJurisdictions
      .map((entry) => entry.Name)
      .filter(Boolean)
    const instrumentNames = instrumentsData
      .map((entry) => entry.Name)
      .filter(Boolean)

    // Merge both lists, remove duplicates, and sort alphabetically
    countries.value = [
      ...new Set([...jurisdictionNames, ...instrumentNames]),
    ].sort((a, b) => a.localeCompare(b))
  } catch (error) {
    console.error(error)
    countries.value = [] // Fallback to empty list
  }
}

// Navigate to country route
const navigateToCountry = async (jurisdiction) => {
  if (!jurisdiction) return

  try {
    // Attempt to fetch country ISO code
    const response = await fetch(
      `https://restcountries.com/v3.1/name/${jurisdiction}?fields=cca2`
    )
    const data = await response.json()

    if (Array.isArray(data) && data.length > 0 && data[0].cca2) {
      // It's a country jurisdiction -> Use ISO2 code (lowercased)
      const isoCode = data[0].cca2.toLowerCase()
      router.push(`/jurisdiction/${isoCode}`)
    } else {
      // It's an International Instrument -> Format name (lowercased, spaces to hyphens)
      const formattedInstrument = jurisdiction
        .toLowerCase()
        .replace(/\s+/g, '-')
      router.push(`/jurisdiction/${formattedInstrument}`)
    }
  } catch (error) {
    console.error(`Error processing jurisdiction: ${jurisdiction}`, error)

    // Assume it's an International Instrument if the country API fails
    const formattedInstrument = jurisdiction.toLowerCase().replace(/\s+/g, '-')
    router.push(`/jurisdiction/${formattedInstrument}`)
  }
}

// Fetch data on mount
onMounted(fetchJurisdictions)
</script>

<style scoped>
.popular-searches-container {
  display: flex;
  flex-wrap: wrap;
}

.popular-title {
  white-space: nowrap; /* Prevents title from wrapping */
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
}
</style>
