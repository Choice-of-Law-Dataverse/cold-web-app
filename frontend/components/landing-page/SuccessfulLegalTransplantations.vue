<template>
  <UCard class="cold-ucard gradient-top-border flex h-full w-full flex-col">
    <div class="flex flex-col gap-4">
      <div>
        <h2 class="card-title">Successful Legal Transplantations</h2>
        <p class="card-subtitle">
          Domestic Instruments compatible with the HCCH Principles
        </p>
      </div>
      <div v-if="isLoading">
        <LoadingLandingPageCard />
      </div>
      <template v-else>
        <div class="flex flex-col gap-2">
          <NuxtLink
            v-for="(instrument, index) in domesticInstruments.slice(0, 9)"
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
import { ref } from "vue";
import LoadingLandingPageCard from "@/components/layout/LoadingLandingPageCard.vue";
import { useDomesticInstruments } from "@/composables/useDomesticInstruments";
import { formatYear } from "@/utils/format";

const filterCompatible = ref(true);
const { data: domesticInstruments, isLoading } = useDomesticInstruments({
  filterCompatible,
});
</script>
