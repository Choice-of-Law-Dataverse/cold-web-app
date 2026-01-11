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
            <UButton class="suggestion-button mt-8" variant="link">
              <img
                :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${decision['Jurisdictions Alpha-3 Code'].toLowerCase()}.svg`"
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
        <div class="mt-8">
          <ShowMoreLess
            v-if="allDecisions.length > 3"
            :isExpanded="showAll"
            label="leading cases"
            @update:isExpanded="showAll = $event"
            buttonClass="suggestion-button"
            iconClass="showmoreless-icon-large"
          />
        </div>
      </template>
    </div>
  </UCard>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRuntimeConfig } from '#app'
import { RouterLink } from 'vue-router'
import LoadingLandingPageCard from '@/components/layout/LoadingLandingPageCard.vue'
import ShowMoreLess from '@/components/ui/ShowMoreLess.vue'

const courtDecisions = ref([])
const allDecisions = ref([])
const isLoading = ref(true)
const showAll = ref(false)
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
      `/api/proxy/search/full_table`,
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
    decisionsData.sort(
      (a, b) =>
        formatYear(b['Publication Date ISO']) -
        formatYear(a['Publication Date ISO'])
    )
    allDecisions.value = decisionsData
    courtDecisions.value = decisionsData.slice(0, 3)
  } catch (error) {
    console.error(error)
    courtDecisions.value = []
    allDecisions.value = []
  } finally {
    isLoading.value = false
  }
}

watch(showAll, (val) => {
  courtDecisions.value = val
    ? allDecisions.value
    : allDecisions.value.slice(0, 3)
})

onMounted(fetchCourtDecisions)
</script>

<style scoped>
.result-value-small {
  line-height: 36px !important;
  margin-bottom: 0px !important;
}
</style>
