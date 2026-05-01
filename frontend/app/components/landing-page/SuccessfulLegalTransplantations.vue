<template>
  <LandingCardShell
    title="Successful Legal Transplantations"
    subtitle="Domestic Instruments compatible with the HCCH Principles"
    :loading="isLoading"
    :error="error"
  >
    <FlagTitleYearItem
      v-for="instrument in domesticInstruments"
      :key="String(instrument.id || '')"
      :to="`/domestic-instrument/${instrument.id}`"
      :iso3="instrument.jurisdictionsAlpha3Code || ''"
      :title="instrument.titleInEnglish || ''"
      :year="
        instrument.entryIntoForce
          ? String(formatYear(instrument.entryIntoForce))
          : instrument.date || ''
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

const filterCompatible = ref(true);
const {
  data: domesticInstruments,
  isLoading,
  error,
} = useDomesticInstruments({
  filterCompatible,
  limit: 9,
});
</script>
