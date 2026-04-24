<template>
  <LandingCardShell
    title="Leading Cases"
    subtitle="Read top-ranked court decisions"
    :loading="isLoading"
    :error="error"
  >
    <FlagTitleYearItem
      v-for="decision in leadingCases"
      :key="String(decision.id || '')"
      :to="`/court-decision/${decision.id}`"
      :iso3="decision.jurisdictionsAlpha3Code || ''"
      :title="decision.caseTitle || ''"
      :year="
        decision.publicationDateIso
          ? String(formatYear(decision.publicationDateIso))
          : decision.date || ''
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
