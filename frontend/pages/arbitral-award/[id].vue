<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="arbitralAward || {}"
      :labels="arbitralAwardLabels"
      :formatted-jurisdiction="arbitralAward?.formattedJurisdictions || []"
      :formatted-theme="arbitralAward?.formattedThemes || []"
      :show-suggest-edit="true"
      source-table="Arbitral Award"
    />

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[
        arbitralAward?.['Case Number'] &&
        String(arbitralAward['Case Number']).trim()
          ? `Case Number ${arbitralAward['Case Number']}`
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
</script>
