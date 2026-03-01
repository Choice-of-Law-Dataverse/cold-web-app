<template>
  <LandingCardShell
    title="Successful Legal Transplantations"
    subtitle="Domestic Instruments compatible with the HCCH Principles"
    :loading="isLoading"
    :error="error"
  >
    <FlagTitleYearItem
      v-for="(instrument, index) in domesticInstruments?.slice(0, 9)"
      :key="index"
      :to="`/domestic-instrument/${instrument.ID}`"
      :iso3="instrument['Jurisdictions Alpha-3 Code'] || ''"
      :title="instrument['Title (in English)'] || ''"
      :year="
        instrument['Entry Into Force']
          ? String(formatYear(instrument['Entry Into Force']))
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

const filterCompatible = ref(true);
const {
  data: domesticInstruments,
  isLoading,
  error,
} = useDomesticInstruments({
  filterCompatible,
});
</script>
