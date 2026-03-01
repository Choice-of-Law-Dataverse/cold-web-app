<template>
  <div class="flex items-start justify-between gap-4">
    <div :class="titleClass">
      <slot />
    </div>
    <div class="flex flex-shrink-0 items-center gap-3">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    titleClass?: string | string[];
  }>(),
  {
    titleClass: "result-value-small flex-1",
  },
);
</script>
