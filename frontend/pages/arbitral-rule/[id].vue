<template>
  <BaseDetailLayout
    :loading="loading"
    :result-data="processedArbitralRule || {}"
    :key-label-pairs="computedKeyLabelPairs"
    :value-class-map="valueClassMap"
    :show-suggest-edit="true"
    source-table="Arbitral Rule"
  />
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import { arbitralRuleConfig } from "@/config/pageConfigs";
import { useSeoMeta } from "#imports";
import type { TableName } from "~/types/api";

interface ArbitralRuleRecord {
  "Set of Rules"?: string;
  related_arbitral_institutions?: Array<{ Institution?: string }>;
  [key: string]: unknown;
}

const route = useRoute();

// Use TanStack Vue Query for data fetching - no need for refs with static values
const table = ref<TableName>("Arbitral Rules");
const id = ref(route.params.id as string);

const { data: arbitralRule, isLoading: loading } = useRecordDetails<ArbitralRuleRecord>(table, id);

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  arbitralRule,
  arbitralRuleConfig,
);

const processedArbitralRule = computed(() => {
  if (!arbitralRule.value) return null;
  return {
    ...arbitralRule.value,
    // Derive flat display field from nested related_arbitral_institutions
    "Arbitral Institution": Array.isArray(
      arbitralRule.value?.related_arbitral_institutions,
    )
      ? arbitralRule.value.related_arbitral_institutions
          .map((inst) => inst?.Institution)
          .filter((v) => v && String(v).trim())
          .join(", ")
      : undefined,
  };
});

// Simplify page title generation
const pageTitle = computed(() => {
  if (!arbitralRule.value) return "Arbitral Rule — CoLD";
  const title = arbitralRule.value["Set of Rules"];
  return title && String(title).trim()
    ? `${title} — CoLD`
    : "Arbitral Rule — CoLD";
});

// Use useSeoMeta for better performance
useSeoMeta({
  title: pageTitle,
  description: pageTitle,
  ogTitle: pageTitle,
  ogDescription: pageTitle,
  twitterTitle: pageTitle,
  twitterDescription: pageTitle,
});

// Canonical URL
useHead({
  link: [
    { rel: "canonical", href: `https://cold.global${route.fullPath}` },
  ],
});
</script>
