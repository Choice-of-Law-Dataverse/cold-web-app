<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container">
      <h2 class="popular-title">Temporary Jurisdiction Picker</h2>
      <div class="suggestions">
        <USelectMenu
          searchable
          searchable-placeholder="Search a Jurisdiction..."
          class="w-72 lg:w-96 cold-uselectmenu"
          placeholder="Pick a Jurisdiction"
          :options="countries"
          v-model="selectedCountry"
          @change="navigateToCountry"
          size="xl"
        />
      </div>
    </div>
  </UCard>
</template>

<script setup>
// Import Nuxt's `useRouter` composable for navigation
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'

// Reactive state
const countries = ref([])
const selectedCountry = ref(null)

// Fetch jurisdictions from the text file
async function fetchJurisdictions() {
  try {
    const response = await fetch('/temp_jurisdictions.txt') // Path to the file in `public`
    if (!response.ok) throw new Error('Failed to load jurisdictions file')
    const text = await response.text()
    countries.value = text
      .split('\n')
      .map((country) => country.trim())
      .filter(Boolean) // Split and clean the list
  } catch (error) {
    console.error(error)
    countries.value = [] // Fallback to an empty list if there's an error
  }
}

// Nuxt Router instance
const router = useRouter()

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

// Load the jurisdictions when the component is mounted
onMounted(() => {
  fetchJurisdictions()
})
</script>

<style scoped>
.popular-searches-container {
  display: flex;
  align-items: center;
  gap: 48px; /* Space between items */
}

.popular-title {
  white-space: nowrap; /* Prevents the title from wrapping to a new line */
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 36px; /* Space between each suggestion link */
}
</style>
