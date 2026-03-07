<template>
  <LandingCardShell
    title="Recent Domestic Instruments"
    subtitle="Newly added legislation"
    :loading="isLoading"
    :error="error"
    header-link="/search?type=Domestic+Instruments&sortBy=date"
    header-class="cursor-pointer text-left md:whitespace-nowrap"
  >
    <FlagTitleYearItem
      v-for="(instrument, index) in domesticInstruments?.slice(0, 3)"
      :key="index"
      :to="`/domestic-instrument/${instrument.ID}`"
      :iso3="instrument.jurisdictionsAlpha3Code || ''"
      :title="instrument.titleInEnglish || ''"
      :year="
        instrument.entryIntoForce
          ? String(formatYear(instrument.entryIntoForce))
          : instrument['Date'] || ''
      "
      type-class="type-instrument"
    />
  </LandingCardShell>
</template>

<script setup lang="ts">
import { ref } from "vue";
import LandingCardShell from "@/components/landing-page/LandingCardShell.vue";
import FlagTitleYearItem from "@/components/landing-page/FlagTitleYearItem.vue";
import { useDomesticInstruments } from "@/composables/useDomesticInstruments";
import { formatYear } from "@/utils/format";

const {
  data: domesticInstruments,
  isLoading,
  error,
} = useDomesticInstruments({
  filterCompatible: ref(false),
});
</script>
