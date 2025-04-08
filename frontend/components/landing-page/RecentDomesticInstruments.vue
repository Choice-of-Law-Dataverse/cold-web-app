<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container flex flex-col md:flex-row gap-8">
      <h2 class="popular-title text-left md:whitespace-nowrap">
        Recent Domestic Instruments
      </h2>
    </div>
    <ul>
      <li v-for="(instrument, index) in domesticInstruments" :key="index">
        <RouterLink :to="`/legal-instrument/${instrument.ID}`">
          <UButton
            class="suggestion-button"
            variant="link"
            icon="i-material-symbols:arrow-forward"
            trailing
          >
            <span class="break-words text-left">
              {{ instrument['Title (in English)'] }}
            </span>
          </UButton>
        </RouterLink>
      </li>
    </ul>
  </UCard>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRuntimeConfig } from '#app'
import { RouterLink } from 'vue-router'

const domesticInstruments = ref([])
const config = useRuntimeConfig()

async function fetchDomesticInstruments() {
  try {
    const payload = { table: 'Domestic Instruments', filters: [] }
    const response = await fetch(
      `${config.public.apiBaseUrl}/search/full_table`,
      {
        method: 'POST',
        headers: {
          authorization: `Bearer ${config.public.FASTAPI}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      }
    )
    if (!response.ok) throw new Error('Failed to load data')
    const instrumentsData = await response.json()
    // Convert Date to number, sort descending and take the 3 most recent
    instrumentsData.sort((a, b) => Number(b.Date) - Number(a.Date))
    domesticInstruments.value = instrumentsData.slice(0, 3)
  } catch (error) {
    console.error(error)
    domesticInstruments.value = []
  }
}

onMounted(fetchDomesticInstruments)
</script>

<style scoped></style>
