<template>
  <div class="py-6">
    <h1 class="card-title mb-1">Leading Cases</h1>
    <p class="card-subtitle mb-8">Top-ranked court decisions</p>

    <div v-if="isLoading" class="results-grid">
      <LoadingCard v-for="n in 6" :key="`loading-${n}`" />
    </div>

    <InlineError v-else-if="error" :error="error" />

    <div v-else-if="!leadingCases?.length" class="py-12 text-center">
      <p class="result-value-small">No leading cases found.</p>
    </div>

    <div v-else class="results-grid">
      <div
        v-for="decision in enrichedLeadingCases"
        :key="String(decision.id || '')"
        class="result-item"
      >
        <SearchResultCardContent
          :result-data="decision as unknown as AnySearchResult"
          card-type="Court Decisions"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import SearchResultCardContent from "@/components/search-results/SearchResultCardContent.vue";
import LoadingCard from "@/components/layout/LoadingCard.vue";
import InlineError from "@/components/ui/InlineError.vue";
import { useLeadingCases } from "@/composables/useFullTable";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";
import type { AnySearchResult } from "@/types/search";
import { useHead } from "#imports";

useHead({
  title: "Leading Cases — CoLD",
});

const { data: leadingCases, isLoading, error } = useLeadingCases();
const { findJurisdictionByCode } = useJurisdictionLookup();

const enrichedLeadingCases = computed(() =>
  leadingCases.value?.map((decision) => ({
    ...decision,
    jurisdictions:
      decision.jurisdictions ||
      findJurisdictionByCode(decision.jurisdictionsAlpha3Code || "")?.name ||
      null,
  })),
);
</script>
