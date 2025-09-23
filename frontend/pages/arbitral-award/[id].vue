<template>
  <BaseDetailLayout
    :loading="loading"
    :result-data="processedArbitralAward"
    :key-label-pairs="computedKeyLabelPairs"
    :value-class-map="valueClassMap"
    :formatted-jurisdiction="formattedJurisdictions"
    :formatted-theme="formattedThemes"
    :show-suggest-edit="true"
    source-table="Arbitral Award"
  />
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import { arbitralAwardConfig } from "@/config/pageConfigs";
import { useHead } from "#imports";

const route = useRoute();

// Use TanStack Vue Query for data fetching
const table = ref("Arbitral Awards");
const id = ref(route.params.id);

const { data: arbitralAward, isLoading: loading } = useRecordDetails(table, id);

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

// Dynamic page title based on Title
watch(
  processedArbitralAward,
  (newVal) => {
    if (!newVal) return;
    const title = newVal["Case Number"];
    const pageTitle =
      title && String(title).trim()
        ? `Arbitral Award Case Number ${title} — CoLD`
        : "Arbitral Award — CoLD";
    useHead({
      title: pageTitle,
      link: [
        { rel: "canonical", href: `https://cold.global${route.fullPath}` },
      ],
      meta: [{ name: "description", content: pageTitle }],
    });
  },
  { immediate: true },
);
</script>
