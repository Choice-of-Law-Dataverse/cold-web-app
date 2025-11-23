<template>
  <UCard class="cold-ucard flex h-full w-full flex-col">
    <div class="flex flex-col gap-4">
      <div>
        <h2 class="popular-title">Successful Legal Transplantations</h2>
        <p class="result-value-small">
          Domestic Instruments compatible with the HCCH Principles
        </p>
      </div>
      <div v-if="isLoading">
        <LoadingLandingPageCard />
      </div>
      <template v-else>
        <div
          v-for="(instrument, index) in domesticInstruments.slice(0, 9)"
          :key="index"
        >
          <NuxtLink :to="`/domestic-instrument/${instrument.ID}`">
            <UButton class="suggestion-button" variant="link">
              <span
                class="mr-3 inline-flex min-w-[40px] items-center justify-center"
              >
                <img
                  :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${instrument['Jurisdictions Alpha-3 Code'].toLowerCase()}.svg`"
                  class="border-cold-gray h-5 border"
                >
              </span>
              <span class="text-left break-words">
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
import { ref } from "vue";
import LoadingLandingPageCard from "@/components/layout/LoadingLandingPageCard.vue";
import { useDomesticInstruments } from "@/composables/useDomesticInstruments";
import { formatYear } from "@/utils/format";

const filterCompatible = ref(true);
const { data: domesticInstruments, isLoading } = useDomesticInstruments({
  filterCompatible,
});
</script>

<style scoped>
.result-value-small {
  line-height: 36px !important;
  margin-bottom: 0px !important;
}
</style>
