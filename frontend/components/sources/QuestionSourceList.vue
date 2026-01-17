<template>
  <div class="prose flex flex-col gap-2">
    <template v-if="fallbackData && fallbackData['Domestic Legal Provisions']">
      <LegalProvisionRenderer
        :value="fallbackData['Domestic Legal Provisions']"
        :fallback-data="fallbackData"
      />
    </template>
    <template
      v-else-if="fallbackData && fallbackData['Domestic Instruments ID']"
    >
      <LegalProvisionRenderer
        skip-article
        :value="fallbackData['Domestic Instruments ID']"
        :fallback-data="fallbackData"
      />
    </template>

    <template v-if="!hasAnySources">
      <p class="result-value-small">—</p>
    </template>
  </div>
</template>

<script setup>
import { computed } from "vue";
import LegalProvisionRenderer from "@/components/legal/LegalProvisionRenderer.vue";

const props = defineProps({
  fallbackData: {
    type: Object,
    required: true,
  },
});

const hasAnySources = computed(() => {
  return !!(
    (props.fallbackData && props.fallbackData["Domestic Legal Provisions"]) ||
    (props.fallbackData && props.fallbackData["Domestic Instruments ID"])
  );
});
</script>
