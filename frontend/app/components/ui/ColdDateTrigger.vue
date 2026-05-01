<template>
  <ColdControlShell
    v-bind="$attrs"
    :icon="icon"
    :label="label"
    :disabled="disabled"
    class="cold-date-trigger-wrap"
  >
    <slot />
  </ColdControlShell>
</template>

<script setup lang="ts">
import ColdControlShell from "@/components/ui/ColdControlShell.vue";

defineOptions({ inheritAttrs: false });

withDefaults(
  defineProps<{
    icon?: string;
    label?: string;
    disabled?: boolean;
  }>(),
  {
    icon: undefined,
    label: undefined,
    disabled: false,
  },
);
</script>

<style>
.cold-date-trigger-wrap {
  justify-content: flex-start;
}

.cold-date-trigger-wrap .iconify,
.cold-date-trigger-wrap svg,
.cold-date-trigger-wrap [class*="icon"] {
  color: var(--color-cold-purple);
  fill: currentColor;
}
</style>
