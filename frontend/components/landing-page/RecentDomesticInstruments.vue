<template>
  <UCard class="cold-ucard flex h-full w-full flex-col">
    <div class="popular-searches-container flex flex-col gap-8 md:flex-row">
      <h2 class="popular-title text-left md:whitespace-nowrap">
        Recent Domestic Instruments
      </h2>
    </div>
    <div>
      <div v-if="isLoading">
        <LoadingLandingPageCard />
      </div>
      <template v-else>
        <div
          v-for="(instrument, index) in domesticInstruments.slice(0, 3)"
          :key="index"
        >
          <RouterLink :to="`/domestic-instrument/${instrument.ID}`">
            <UButton class="suggestion-button mt-8" variant="link">
              <img
                :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${instrument['Jurisdictions Alpha-3 Code'].toLowerCase()}.svg`"
                class="mr-3 h-5 border border-cold-gray"
              >
              <span class="break-words text-left">
                {{
                  instrument["Entry Into Force"]
                    ? formatYear(instrument["Entry Into Force"])
                    : instrument["Date"]
                }}:
                {{ instrument["Title (in English)"] }}
              </span>
            </UButton>
          </RouterLink>
        </div>
        <UButton
          to="/search?type=Domestic+Instruments&sortBy=date"
          class="suggestion-button mt-8"
          variant="link"
          icon="i-material-symbols:arrow-forward"
          trailing
        >
          See all
        </UButton>
      </template>
    </div>
  </UCard>
</template>

<script setup>
import { RouterLink } from "vue-router";
import LoadingLandingPageCard from "@/components/layout/LoadingLandingPageCard.vue";
import { useDomesticInstruments } from "@/composables/useDomesticInstruments";

const { data: domesticInstruments, isLoading } = useDomesticInstruments({
  filterCompatible: false,
});
</script>

<style scoped></style>
