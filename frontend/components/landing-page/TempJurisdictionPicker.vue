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
import JurisdictionSelectMenu from '@/components/jurisdiction-comparison/JurisdictionSelectMenu.vue'
import { useJurisdictions } from '@/composables/useJurisdictions'

const router = useRouter()

const { data: countries } = useJurisdictions()

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
