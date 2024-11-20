<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container">
      <h2 class="popular-title">Temporary Jurisdiction Selector</h2>
      <div class="suggestions">
        <USelectMenu
          searchable
          searchable-placeholder="Search a jurisdiction..."
          class="w-72 lg:w-96"
          placeholder="Select a jurisdiction"
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

// Reactive state for the selected country
const selectedCountry = ref(null)

// List of countries to display in the menu
const countries = ref([
  'United States',
  'United Kingdom',
  'Germany',
  'France',
  'Switzerland',
  'Australia',
  'Canada',
  'China',
  'India',
  'Japan',
])

// Nuxt Router instance
const router = useRouter()

// Navigate to the selected country's page
const navigateToCountry = (country) => {
  if (country) {
    const formattedCountry = country.replace(/\s+/g, '-').toLowerCase() // Format the country name
    router.push(`/jurisdiction/${formattedCountry}`)
  }
}
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
