<template>
  <component :is="as" :class="sizeClass"><slot /></component>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    size?: "default" | "lg" | "md" | "sm" | "cite";
    as?: string;
  }>(),
  { size: "default", as: "div" },
);

const sizeClass = computed(() => {
  switch (props.size) {
    case "lg":
      return "result-value-large";
    case "md":
      return "result-value-medium";
    case "sm":
      return "result-value-small";
    case "cite":
      return "result-value-small-citation";
    default:
      return "result-value";
  }
});
</script>
