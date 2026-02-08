<template>
  <UCard class="flex h-full w-full" :ui="{ body: '!p-0' }">
    <div class="gradient-top-border" />
    <div class="flex w-full flex-col gap-4 p-4 sm:p-6">
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
      <InlineError v-else-if="error" :error="error" />
      <template v-else-if="domesticInstruments">
        <div class="flex w-full flex-col gap-2">
          <NuxtLink
            v-for="(instrument, index) in domesticInstruments.slice(0, 3)"
            :key="index"
            :to="`/domestic-instrument/${instrument.ID}`"
            class="landing-item-button type-instrument w-full"
          >
            <div class="flag-wrapper">
              <JurisdictionFlag
                :iso3="instrument['Jurisdictions Alpha-3 Code']"
                class="item-flag"
              />
            </div>
            <span class="item-title">
              {{ instrument["Title (in English)"] }}
            </span>
            <span class="item-year">
              {{
                instrument["Entry Into Force"]
                  ? formatYear(instrument["Entry Into Force"])
                  : instrument["Date"]
              }}
            </span>
          </NuxtLink>
        </div>
      </template>
    </div>
  </UCard>
</template>

<script setup>
import LoadingLandingPageCard from "@/components/layout/LoadingLandingPageCard.vue";
import InlineError from "@/components/ui/InlineError.vue";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";
import { useDomesticInstruments } from "@/composables/useDomesticInstruments";
import { formatYear } from "@/utils/format";

const {
  data: domesticInstruments,
  isLoading,
  error,
} = useDomesticInstruments({
  filterCompatible: false,
});
</script>
