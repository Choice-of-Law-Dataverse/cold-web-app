<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="processedArbitralRule || {}"
      :labels="arbitralRuleLabels"
      :show-suggest-edit="true"
      source-table="Arbitral Rule"
    />

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[arbitralRule?.['Set of Rules'] as string]"
      fallback="Arbitral Rule"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import type { TableName } from "@/types/api";
import { arbitralRuleLabels } from "@/config/labels";

interface ArbitralRuleRecord {
  "Set of Rules"?: string;
  related_arbitral_institutions?: Array<{ Institution?: string }>;
  [key: string]: unknown;
}

const route = useRoute();

const table = ref<TableName>("Arbitral Rules");
const id = ref(route.params.id as string);

const { data: arbitralRule, isLoading: loading } =
  useRecordDetails<ArbitralRuleRecord>(table, id);

const processedArbitralRule = computed(() => {
  if (!arbitralRule.value) return null;
  return {
    ...arbitralRule.value,
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
</script>
