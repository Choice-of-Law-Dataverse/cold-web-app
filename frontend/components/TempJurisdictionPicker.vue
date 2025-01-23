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

// Reactive states
const countries = ref([])
const router = useRouter()

// Fetch jurisdictions from the text file
async function fetchJurisdictions() {
  try {
    const response = await fetch('/temp_jurisdictions.txt') // Path to file in `public`
    if (!response.ok) throw new Error('Failed to load jurisdictions file')
    const text = await response.text()
    countries.value = text
      .split('\n')
      .map((country) => country.trim())
      .filter(Boolean) // Clean up list
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
