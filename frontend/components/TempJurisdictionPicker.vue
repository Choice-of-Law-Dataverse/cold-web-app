<template>
  <UCard class="cold-ucard">
    <div
      class="popular-searches-container flex flex-col md:flex-row gap-6 md:items-center"
    >
      <h2 class="popular-title">Temporary Jurisdiction Picker</h2>
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
    const jsonPayload = {
      table: 'Jurisdictions',
      filters: [],
    }

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

    if (!response.ok) throw new Error('Failed to load jurisdictions')

    const data = await response.json()

    // Filter out jurisdictions where "Irrelevant?" is explicitly true
    const relevantJurisdictions = data.filter(
      (entry) => entry['Irrelevant?'] === null
    )

    // Extract the "Name" field
    countries.value = relevantJurisdictions
      .map((entry) => entry.Name)
      .filter(Boolean)
      .sort((a, b) => a.localeCompare(b)) // Sort alphabetically
  } catch (error) {
    console.error(error)
    countries.value = [] // Fallback to empty list
  }
}

// Navigate to country route
const navigateToCountry = async (country) => {
  if (country) {
    try {
      const response = await fetch(
        `https://restcountries.com/v3.1/name/${country}?fields=cca2`
      )
      const data = await response.json()

      if (data && data[0] && data[0].cca2) {
        const isoCode = data[0].cca2.toLowerCase() // Convert to lowercase
        router.push(`/jurisdiction/${isoCode}`)
      } else {
        console.error(`ISO2 code not found for country: ${country}`)
      }
    } catch (error) {
      console.error('Error fetching ISO2 code:', error)
    }
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
