<template>
  <UCard class="cold-ucard landing-card flex h-full w-full">
    <div class="flex flex-col gap-4">
      <NuxtLink
        :to="`/search?type=Domestic+Instruments&sortBy=date`"
        class="no-underline"
      >
        <div>
          <h2 class="card-title cursor-pointer text-left md:whitespace-nowrap">
            Recent Domestic Instruments
          </h2>
          <p class="card-subtitle">Newly added legislation</p>
        </div>
      </NuxtLink>

      <div v-if="isLoading">
        <LoadingLandingPageCard />
      </div>
      <template v-else>
        <div class="flex flex-col gap-2">
          <NuxtLink
            v-for="(instrument, index) in domesticInstruments.slice(0, 3)"
            :key="index"
            :to="`/domestic-instrument/${instrument.ID}`"
            class="landing-item-button"
          >
            <div class="flag-wrapper">
              <img
                :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${instrument['Jurisdictions Alpha-3 Code'].toLowerCase()}.svg`"
                class="item-flag"
              />
            </div>
            <span class="break-words text-left">
              {{
                instrument["Entry Into Force"]
                  ? formatYear(instrument["Entry Into Force"])
                  : instrument["Date"]
              }}:
              {{ instrument["Title (in English)"] }}
            </span>
          </NuxtLink>
        </div>
      </template>
    </div>
  </UCard>
</template>

<script setup>
import LoadingLandingPageCard from "@/components/layout/LoadingLandingPageCard.vue";
import { useDomesticInstruments } from "@/composables/useDomesticInstruments";
import { formatYear } from "@/utils/format";

const { data: domesticInstruments, isLoading } = useDomesticInstruments({
  filterCompatible: false,
});
</script>
