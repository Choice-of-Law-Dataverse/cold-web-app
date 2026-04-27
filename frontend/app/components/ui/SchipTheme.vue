<template>
  <SchipShell
    :to="to"
    :is-static="isStatic"
    :compact="compact"
    tone="var(--color-cold-purple)"
  >
    <span class="schip-tag" aria-hidden="true">
      <UIcon name="i-lucide:bookmark" />
    </span>
    <slot />
    <span v-if="!isStatic" class="schip-affordance" aria-hidden="true">
      <UIcon name="i-material-symbols:search" />
    </span>
  </SchipShell>
</template>

<script setup lang="ts">
import SchipShell from "@/components/ui/SchipShell.vue";

withDefaults(
  defineProps<{
    to?: string;
    isStatic?: boolean;
    compact?: boolean;
  }>(),
  {
    to: "",
    isStatic: false,
    compact: false,
  },
);
</script>
