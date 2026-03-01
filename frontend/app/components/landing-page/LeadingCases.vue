<template>
  <LandingCardShell
    title="Leading Cases"
    subtitle="Read top-ranked court decisions"
    :loading="isLoading"
    :error="error"
  >
    <FlagTitleYearItem
      v-for="(decision, index) in leadingCases?.slice(0, 3)"
      :key="index"
      :to="`/court-decision/${decision.ID}`"
      :iso3="decision['Jurisdictions Alpha-3 Code'] || ''"
      :title="decision['Case Title'] || ''"
      :year="
        decision['Publication Date ISO']
          ? String(formatYear(decision['Publication Date ISO']))
          : decision['Date'] || ''
      "
      type-class="type-court-decision"
    />
  </LandingCardShell>
</template>

<script setup lang="ts">
import LandingCardShell from "@/components/landing-page/LandingCardShell.vue";
import FlagTitleYearItem from "@/components/landing-page/FlagTitleYearItem.vue";
import { useLeadingCases } from "@/composables/useFullTable";
import { formatYear } from "@/utils/format";

const { data: leadingCases, isLoading, error } = useLeadingCases();
</script>
