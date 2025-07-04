<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">Successful Legal Transplantations</h2>
    <p class="result-value-small">
      Domestic Instruments compatible with the HCCH Principles
    </p>
    <div>
      <div v-if="isLoading">
        <LoadingLandingPageCard />
      </div>
      <template v-else>
        <div v-for="(instrument, index) in domesticInstruments" :key="index">
          <RouterLink :to="`/domestic-instrument/${instrument.ID}`">
            <UButton class="suggestion-button mt-6" variant="link">
              <img
                :src="`https://choiceoflawdataverse.blob.core.windows.net/assets/flags/${instrument['Jurisdictions Alpha-3 Code'].toLowerCase()}.svg`"
                style="height: 20px; border: 1px solid var(--color-cold-gray)"
                class="mr-3"
              />
              <span class="break-words text-left">
                {{
                  instrument['Entry Into Force']
                    ? formatYear(instrument['Entry Into Force'])
                    : instrument['Date']
                }}:
                {{ instrument['Title (in English)'] }}
              </span>
            </UButton>
          </RouterLink>
        </div>
      </template>
    </div>
  </UCard>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRuntimeConfig } from '#app'
import { RouterLink } from 'vue-router'
import LoadingLandingPageCard from '@/components/layout/LoadingLandingPageCard.vue'

const domesticInstruments = ref([])
const isLoading = ref(true) // Added loading state
const config = useRuntimeConfig()

async function fetchDomesticInstruments() {
  try {
    const payload = {
      table: 'Domestic Instruments',
      filters: [
        {
          column: 'Compatible With the HCCH Principles?',
          value: true,
        },
      ],
    }
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
    // Convert Date to number, sort descending and take the n most recent
    instrumentsData.sort((a, b) => Number(b.Date) - Number(a.Date))
    domesticInstruments.value = instrumentsData.slice(0, 7)
  } catch (error) {
    console.error(error)
    domesticInstruments.value = []
  } finally {
    isLoading.value = false // Set loading to false once finished
  }
}

onMounted(fetchDomesticInstruments)
</script>

<style scoped>
.result-value-small {
  line-height: 36px !important;
  margin-bottom: 0px !important;
}
</style>
