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
        <div
          v-for="(instrument, index) in domesticInstruments.slice(0, 7)"
          :key="index"
        >
          <RouterLink :to="`/domestic-instrument/${instrument.ID}`">
            <UButton class="suggestion-button mt-6" variant="link">
              <img
                :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${instrument['Jurisdictions Alpha-3 Code'].toLowerCase()}.svg`"
                class="mr-3 h-5 border border-cold-gray"
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
import { RouterLink } from 'vue-router'
import LoadingLandingPageCard from '@/components/layout/LoadingLandingPageCard.vue'
import { useDomesticInstruments } from '@/composables/useDomesticInstruments'
import { formatYear } from '@/utils/format'

const { data: domesticInstruments, isLoading } = useDomesticInstruments({
  filterCompatible: true,
})
</script>

<style scoped>
.result-value-small {
  line-height: 36px !important;
  margin-bottom: 0px !important;
}
</style>
