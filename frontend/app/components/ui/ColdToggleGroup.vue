<template>
  <div class="cold-toggle-group-wrap" role="group" :aria-label="label">
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    label?: string;
  }>(),
  {
    label: undefined,
  },
);
</script>

<style>
.cold-toggle-group-wrap {
  @apply grid w-full gap-2;
  grid-template-columns: 1fr 1fr;
}
</style>
