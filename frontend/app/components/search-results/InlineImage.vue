<template>
  <span v-if="field.inlineImage && displayData[field.inlineImage.dataKey]">
    <img
      :class="field.inlineImage.class"
      :src="field.inlineImage.src"
      :alt="field.inlineImage.alt"
    />
  </span>
</template>

<script setup lang="ts">
import type { SearchCardField } from "@/config/entityRegistry";

defineProps<{
  field: SearchCardField;
  displayData: Record<string, unknown>;
}>();
</script>
