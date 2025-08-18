<template>
  <UCard class="cold-ucard">
    <div
      class="popular-searches-container flex flex-col md:flex-row gap-6 md:items-center"
    >
      <h2 class="popular-title">Open a Country Report</h2>
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
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import JurisdictionSelectMenu from '@/components/jurisdiction-comparison/JurisdictionSelectMenu.vue'
import { useRuntimeConfig } from '#app'

// Reactive states
const countries = ref([])
const router = useRouter()
const config = useRuntimeConfig()

// Fetch jurisdictions from the text file
async function fetchJurisdictions() {
  try {
    const jsonPayloads = [{ table: 'Jurisdictions', filters: [] }]

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
      (entry) => entry['Irrelevant?'] === false
    )
    console.log('relevantJurisdictions:', relevantJurisdictions)

    // Extract "Name" field
    const jurisdictionNames = relevantJurisdictions
      .map((entry) => entry.Name)
      .filter(Boolean)
    console.log('jurisdictionNames:', jurisdictionNames)

    // Merge both lists, remove duplicates, and sort alphabetically
    countries.value = [
      ...new Set([...jurisdictionNames]), // ...instrumentNames]),
    ].sort((a, b) => a.localeCompare(b))
    console.log('countries:', countries.value)
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
        `https://restcountries.com/v3.1/name/${country}?fields=cca3`
      )
      const data = await response.json()

      if (data && data[0] && data[0].cca3) {
        const isoCode = data[0].cca3.toLowerCase() // Convert to lowercase
        router.push(`/jurisdiction/${isoCode}`)
      } else {
        console.error(`ISO3 code not found for country: ${country}`)
      }
    } catch (error) {
      console.error('Error fetching ISO3 code:', error)
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
