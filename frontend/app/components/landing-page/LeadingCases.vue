<template>
  <LandingCardShell
    title="Leading Cases"
    subtitle="Read top-ranked court decisions"
    :loading="isLoading"
    :error="error"
    header-link="/court-decision?caseRank=10"
    header-class="cursor-pointer text-left md:whitespace-nowrap"
  >
    <FlagTitleYearItem
      v-for="decision in leadingCases"
      :key="String(decision.coldId || decision.id || '')"
      :to="`/court-decision/${decision.coldId}`"
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
import { computed } from "vue";
import LandingCardShell from "@/components/landing-page/LandingCardShell.vue";
import FlagTitleYearItem from "@/components/landing-page/FlagTitleYearItem.vue";
import { useEntityList } from "@/composables/useEntityList";
import { formatYear } from "@/utils/format";

const { data, isLoading, error } = useEntityList("court-decisions", {
  caseRank: "10",
  pageSize: 6,
});

const leadingCases = computed(() => data.value?.items ?? []);
</script>
