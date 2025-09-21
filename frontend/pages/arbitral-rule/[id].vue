<template>
  <BaseDetailLayout
    :loading="loading"
    :resultData="processedArbitralRule"
    :keyLabelPairs="computedKeyLabelPairs"
    :valueClassMap="valueClassMap"
    :showSuggestEdit="true"
    sourceTable="Arbitral Rule"
  />
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import { arbitralRuleConfig } from "@/config/pageConfigs";
import { useHead } from "#imports";

const route = useRoute();

// Use TanStack Vue Query for data fetching
const table = ref("Arbitral Rules");
const id = ref(route.params.id);

const {
  data: arbitralRule,
  isLoading: loading,
  error,
} = useRecordDetails(table, id);

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

// Dynamic page title based on Set_of_Rules
watch(
  arbitralRule,
  (newVal) => {
    if (!newVal) return;
    const title = newVal["Set of Rules"];
    const pageTitle =
      title && String(title).trim()
        ? `${title} — CoLD`
        : "Arbitral Rule — CoLD";
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
