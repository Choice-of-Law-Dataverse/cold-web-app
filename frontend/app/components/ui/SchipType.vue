<template>
  <SchipShell
    ref="shell"
    :to="to"
    :as-button="asButton"
    :is-static="isStatic"
    :compact="compact"
    :tone="tone"
  >
    <span v-if="!asButton" class="schip-tag" aria-hidden="true">
      <UIcon name="i-lucide:tag" />
    </span>
    <slot />
    <span
      v-if="!asButton && !isStatic"
      class="schip-affordance"
      aria-hidden="true"
    >
      <UIcon name="i-material-symbols:arrow-forward" />
    </span>
  </SchipShell>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import SchipShell from "@/components/ui/SchipShell.vue";

const TYPE_TONE: Record<string, string> = {
  "label-court-decision": "var(--color-label-court-decision)",
  "label-question": "var(--color-label-question)",
  "label-instrument": "var(--color-label-instrument)",
  "label-arbitration": "var(--color-label-arbitration)",
  "label-literature": "var(--color-label-literature)",
  "label-specialist": "var(--color-label-specialist)",
  "label-jurisdiction": "var(--color-cold-night)",
};

const props = withDefaults(
  defineProps<{
    colorClass?: string;
    to?: string;
    asButton?: boolean;
    isStatic?: boolean;
    compact?: boolean;
  }>(),
  {
    colorClass: "",
    to: "",
    asButton: false,
    isStatic: false,
    compact: false,
  },
);

const tone = computed(
  () => TYPE_TONE[props.colorClass] ?? "var(--color-cold-purple)",
);

const shell = ref<InstanceType<typeof SchipShell> | null>(null);
const rootEl = computed(() => shell.value?.rootEl ?? null);
defineExpose({ rootEl });
</script>
