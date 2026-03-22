<template>
  <span v-if="showImage">
    <img
      :class="field.inlineImage!.class"
      :src="field.inlineImage!.src"
      :alt="field.inlineImage!.alt"
    />
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { SearchCardField } from "@/config/entityRegistry";
import { searchResultField, type AnySearchResult } from "@/types/search";

const props = defineProps<{
  field: SearchCardField;
  displayData: AnySearchResult;
}>();

const showImage = computed(() => {
  if (!props.field.inlineImage) return false;
  return Boolean(
    searchResultField(props.displayData, props.field.inlineImage.dataKey),
  );
});
</script>
