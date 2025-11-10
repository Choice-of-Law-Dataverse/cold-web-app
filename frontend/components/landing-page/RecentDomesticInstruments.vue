<template>
  <UCard class="cold-ucard flex h-full w-full">
    <div class="flex flex-col gap-4">
      <NuxtLink
        :to="`/search?type=Domestic+Instruments&sortBy=date`"
        class="no-underline"
      >
        <div>
          <h2
            class="popular-title cursor-pointer text-left md:whitespace-nowrap"
          >
            Recent Domestic Instruments
          </h2>
          <p class="result-value-small">Newly added legislation</p>
        </div>
      </NuxtLink>

      <div v-if="isLoading">
        <LoadingLandingPageCard />
      </div>
      <template v-else>
        <div
          v-for="(instrument, index) in domesticInstruments.slice(0, 3)"
          :key="index"
        >
          <NuxtLink :to="`/domestic-instrument/${instrument.ID}`">
            <UButton class="suggestion-button" variant="link">
              <span
                class="mr-3 inline-flex min-w-[40px] items-center justify-center"
              >
                <img
                  :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${instrument['Jurisdictions Alpha-3 Code'].toLowerCase()}.svg`"
                  class="h-5 border border-cold-gray"
                >
              </span>
              <span class="break-words text-left">
                {{
                  instrument["Entry Into Force"]
                    ? formatYear(instrument["Entry Into Force"])
                    : instrument["Date"]
                }}:
                {{ instrument["Title (in English)"] }}
              </span>
            </UButton>
          </NuxtLink>
        </div>
      </template>
    </div>
  </UCard>
</template>

<script setup>
import LoadingLandingPageCard from "@/components/layout/LoadingLandingPageCard.vue";
import { useDomesticInstruments } from "@/composables/useDomesticInstruments";

const { data: domesticInstruments, isLoading } = useDomesticInstruments({
  filterCompatible: false,
});
</script>

<style scoped></style>
