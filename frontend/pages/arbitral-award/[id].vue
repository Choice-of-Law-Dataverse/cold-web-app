<template>
  <BaseDetailLayout
    :loading="loading"
    :result-data="processedArbitralAward || {}"
    :key-label-pairs="computedKeyLabelPairs"
    :value-class-map="valueClassMap"
    :formatted-jurisdiction="formattedJurisdictions"
    :formatted-theme="formattedThemes"
    :show-suggest-edit="true"
    source-table="Arbitral Award"
  />
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import { arbitralAwardConfig } from "@/config/pageConfigs";
import { useSeoMeta } from "#imports";
import type { TableName } from "~/types/api";

interface ArbitralAwardRecord {
  "Case Number"?: string;
  [key: string]: unknown;
}

const route = useRoute();

// Use TanStack Vue Query for data fetching - no need for refs with static values
const table = ref<TableName>("Arbitral Awards");
const id = ref(route.params.id as string);

const { data: arbitralAward, isLoading: loading } = useRecordDetails<ArbitralAwardRecord>(table, id);

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  arbitralAward,
  arbitralAwardConfig,
);

const processedArbitralAward = computed(() => {
  if (!arbitralAward.value) return null;
  const raw = arbitralAward.value;
  const derivedTitle =
    raw["Award Title"] || raw["Case Title"] || raw["Title"] || raw["Name"];
  return {
    ...raw,
    Title: derivedTitle,
    // Flatten potential nested institutions like in rules
    "Arbitral Institution": Array.isArray(raw?.related_arbitral_institutions)
      ? raw.related_arbitral_institutions
          .map((inst) => inst?.Institution)
          .filter((v) => v && String(v).trim())
          .join(", ")
      : undefined,
  };
});

// Jurisdictions for header labels
const formattedJurisdictions = computed(() => {
  const list = arbitralAward.value?.related_jurisdictions;
  if (!Array.isArray(list)) return [];
  const names = list
    .map((j) => j?.Name)
    .filter((n) => n && String(n).trim())
    .map((n) => String(n).trim());
  return [...new Set(names)];
});

// Themes for header labels
const formattedThemes = computed(() => {
  const list = arbitralAward.value?.related_themes;
  if (!Array.isArray(list)) return [];
  const themes = list
    .map((t) => t?.Theme)
    .filter((n) => n && String(n).trim())
    .map((n) => String(n).trim());
  return [...new Set(themes)];
});

// Simplify page title generation with computed property
const pageTitle = computed(() => {
  if (!processedArbitralAward.value) return "Arbitral Award — CoLD";
  const title = processedArbitralAward.value["Case Number"];
  return title && String(title).trim()
    ? `Arbitral Award Case Number ${title} — CoLD`
    : "Arbitral Award — CoLD";
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
