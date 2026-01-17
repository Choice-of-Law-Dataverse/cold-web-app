<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="processedArbitralAward || {}"
      :labels="arbitralAwardLabels"
      :formatted-jurisdiction="formattedJurisdictions || []"
      :formatted-theme="formattedThemes || []"
      :show-suggest-edit="true"
      source-table="Arbitral Award"
    />

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[
        processedArbitralAward?.['Case Number'] &&
        String(processedArbitralAward['Case Number']).trim()
          ? `Case Number ${processedArbitralAward['Case Number']}`
          : null,
      ]"
      fallback="Arbitral Award"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useArbitralAward } from "@/composables/useArbitralAward";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { arbitralAwardLabels } from "@/config/labels";

const route = useRoute();

const { data: arbitralAward, isLoading: loading } = useArbitralAward(
  computed(() => route.params.id as string),
);

const processedArbitralAward = computed(() => {
  if (!arbitralAward.value) return null;
  const raw = arbitralAward.value;
  const derivedTitle =
    raw["Award Title"] || raw["Case Title"] || raw["Title"] || raw["Name"];
  return {
    ...raw,
    Title: derivedTitle,
    "Arbitral Institution": Array.isArray(raw?.related_arbitral_institutions)
      ? raw.related_arbitral_institutions
          .map((inst) => inst?.Institution)
          .filter((v) => v && String(v).trim())
          .join(", ")
      : undefined,
  };
});

const formattedJurisdictions = computed(() => {
  const list = arbitralAward.value?.related_jurisdictions;
  if (!Array.isArray(list)) return [];
  const names = list
    .map((j) => j?.Name)
    .filter((n) => n && String(n).trim())
    .map((n) => String(n).trim());
  return [...new Set(names)].map((name) => ({ Name: name }));
});

const formattedThemes = computed(() => {
  const list = arbitralAward.value?.related_themes;
  if (!Array.isArray(list)) return [];
  const themes = list
    .map((t) => t?.Theme)
    .filter((n) => n && String(n).trim())
    .map((n) => String(n).trim());
  return [...new Set(themes)].map((theme) => ({ Theme: theme }));
});
</script>
