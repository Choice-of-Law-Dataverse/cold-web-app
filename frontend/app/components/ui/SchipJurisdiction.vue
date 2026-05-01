<template>
  <SchipShell :to="to" :compact="compact" tone="var(--color-cold-night)">
    <span class="schip-flag-wrap">
      <JurisdictionFlag v-if="iso3" :iso3="iso3" class="schip-flag" />
    </span>
    <slot />
    <span class="schip-arrow-wrap" aria-hidden="true">
      <UIcon name="i-material-symbols:arrow-forward" />
    </span>
  </SchipShell>
</template>

<script setup lang="ts">
import SchipShell from "@/components/ui/SchipShell.vue";
import JurisdictionFlag from "@/components/ui/JurisdictionFlag.vue";

withDefaults(
  defineProps<{
    iso3: string;
    to: string;
    compact?: boolean;
  }>(),
  {
    compact: false,
  },
);
</script>
