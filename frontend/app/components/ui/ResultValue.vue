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

<style>
@reference "tailwindcss";

.result-value {
  @apply font-medium;
  color: var(--color-cold-night);
  word-wrap: break-word;
  word-break: break-word;
  white-space: pre-wrap;
}

.result-value-large {
  @apply text-base leading-[1.7] font-medium whitespace-normal;
  color: var(--color-cold-night);
  overflow-wrap: break-word;
}

.result-value-medium {
  @apply leading-[1.7] font-medium whitespace-normal;
  color: var(--color-cold-night);
  overflow-wrap: break-word;
  font-size: 0.9375rem;
}

.result-value-small {
  @apply text-sm leading-[1.7] font-medium whitespace-normal;
  color: var(--color-cold-night);
  word-wrap: break-word;
  word-break: break-word;
}

.result-value-small-citation {
  @apply text-[0.8125rem] leading-[1.6] font-medium whitespace-normal;
  color: var(--color-cold-night);
  word-wrap: break-word;
  word-break: break-word;
  font-family: "IBM Plex Mono", monospace;
  background: var(--gradient-gray);
  padding: 1em 1.25em;
  border-radius: 0.5rem;
  border: 1px solid var(--color-cold-gray);
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.03);
}
</style>
