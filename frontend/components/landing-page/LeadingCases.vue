<template>
  <UCard class="cold-ucard">
    <h2 class="popular-title">Leading Cases</h2>
    <p class="result-value-small">Court decisions ranked highly in CoLD</p>
    <div>
      <div v-if="isLoading">
        <LoadingLandingPageCard />
      </div>
      <template v-else>
        <div v-for="(decision, index) in courtDecisions" :key="index">
          <RouterLink :to="`/court-decision/${decision.ID}`">
            <UButton
              class="suggestion-button mt-8"
              variant="link"
              icon="i-material-symbols:arrow-forward"
              trailing
            >
              <img
                :src="`https://choiceoflawdataverse.blob.core.windows.net/assets/flags/${decision['Jurisdictions Alpha-3 Code'].toLowerCase()}.svg`"
                style="height: 20px; border: 1px solid var(--color-cold-gray)"
                class="mr-3"
              />
              <span class="break-words text-left">
                {{
                  decision['Publication Date ISO']
                    ? formatYear(decision['Publication Date ISO'])
                    : decision['Date']
                }}:
                {{ decision['Case Title'] }}
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
import LoadingLandingPageCard from '../layout/LoadingLandingPageCard.vue'

const courtDecisions = ref([])
const isLoading = ref(true) // Added loading state
const config = useRuntimeConfig()

async function fetchCourtDecisions() {
  try {
    const payload = {
      table: 'Court Decisions',
      filters: [
        {
          column: 'Case Rank',
          value: 10,
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
    const decisionsData = await response.json()
    // Convert Date to number, sort descending and take the n most recent
    decisionsData.sort(
      (a, b) =>
        formatYear(b['Publication Date ISO']) -
        formatYear(a['Publication Date ISO'])
    )
    courtDecisions.value = decisionsData.slice(0, 3)
  } catch (error) {
    console.error(error)
    courtDecisions.value = []
  } finally {
    isLoading.value = false // Set loading to false once finished
  }
}

onMounted(fetchCourtDecisions)
</script>

<style scoped>
.result-value-small {
  line-height: 36px !important;
  margin-bottom: 0px !important;
}
</style>
