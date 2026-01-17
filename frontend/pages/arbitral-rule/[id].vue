<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="arbitralRule || {}"
      :labels="arbitralRuleLabels"
      :show-suggest-edit="true"
      source-table="Arbitral Rule"
    />

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[arbitralRule?.['Set of Rules']]"
      fallback="Arbitral Rule"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useArbitralRule } from "@/composables/useArbitralRule";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { arbitralRuleLabels } from "@/config/labels";

const route = useRoute();

const { data: arbitralRule, isLoading: loading } = useArbitralRule(
  computed(() => route.params.id as string),
);
</script>
