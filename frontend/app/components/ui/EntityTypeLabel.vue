<template>
  <span :class="['entity-type-label', variantClass]">
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";

const VARIANT_COLOR_MAP: Record<string, string> = {
  question: "entity-type-label--question",
  "court-decision": "entity-type-label--court-decision",
  instrument: "entity-type-label--instrument",
  literature: "entity-type-label--literature",
  "oup-chapter": "entity-type-label--oup-chapter",
  arbitration: "entity-type-label--arbitration",
  specialist: "entity-type-label--specialist",
  theme: "entity-type-label--theme",
};

const props = withDefaults(
  defineProps<{
    variant: string;
  }>(),
  {},
);

const variantClass = computed(() => VARIANT_COLOR_MAP[props.variant] ?? "");
</script>

<style>
@reference "tailwindcss";

.entity-type-label {
  --label-color: var(--color-cold-purple);
  @apply inline-flex gap-1 font-mono text-xs font-medium tracking-widest uppercase;
  color: var(--color-cold-night);
  padding: 4px 10px;
  border-radius: 4px;
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--label-color) 8%, white),
    color-mix(in srgb, var(--label-color) 4%, white)
  );
  border: 1px solid color-mix(in srgb, var(--label-color) 12%, transparent);
  transition: all 0.15s ease;
}

.entity-type-label:hover {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--label-color) 14%, white),
    color-mix(in srgb, var(--label-color) 8%, white)
  );
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.06);
}

.entity-type-label--question {
  --label-color: var(--label-color-question);
}

.entity-type-label--court-decision {
  --label-color: var(--label-color-court-decision);
}

.entity-type-label--instrument {
  --label-color: var(--label-color-instrument);
}

.entity-type-label--literature {
  --label-color: var(--label-color-literature);
}

.entity-type-label--oup-chapter {
  --label-color: var(--label-color-oup-chapter);
}

.entity-type-label--arbitration {
  --label-color: var(--label-color-arbitration);
}

.entity-type-label--specialist {
  --label-color: var(--label-color-specialist);
}

.entity-type-label--theme {
  --label-color: var(--label-color-theme);
}
</style>
