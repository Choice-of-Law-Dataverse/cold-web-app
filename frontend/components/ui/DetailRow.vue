<template>
  <div
    class="detail-row flex flex-col gap-3 md:flex-row md:items-start md:gap-10"
    :class="variant ? `detail-row--${variant}` : ''"
  >
    <div class="label-key md:w-48 md:flex-shrink-0">
      <span class="flex items-center gap-1.5">
        <span class="mono-font">
          {{ label }}
        </span>
        <slot name="label-actions" />
        <InfoPopover v-if="tooltip" :text="tooltip" />
      </span>
    </div>

    <div class="detail-value md:flex-1">
      <slot />
    </div>
  </div>
</template>

<script setup>
import InfoPopover from "@/components/ui/InfoPopover.vue";

defineProps({
  label: {
    type: String,
    required: true,
  },
  tooltip: {
    type: String,
    default: undefined,
  },
  variant: {
    type: String,
    default: undefined,
    validator: (value) =>
      [
        "court-decision",
        "question",
        "instrument",
        "literature",
        "oup",
        "arbitration",
        "jurisdiction",
      ].includes(value),
  },
});
</script>

<style scoped>
.detail-row {
  padding: 0.75rem 1rem;
  margin: 0 -1rem;
  border-radius: 2px;
  border-left: 2px solid transparent;
  transition: background 0.15s ease;
}

.detail-row:hover {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-purple) 3%, white),
    color-mix(in srgb, var(--color-cold-green) 2%, white)
  );
}

.detail-row--court-decision {
  border-left-color: var(--color-label-court-decision);
}

.detail-row--question {
  border-left-color: var(--color-label-question);
}

.detail-row--instrument {
  border-left-color: var(--color-label-instrument);
}

.detail-row--literature {
  border-left-color: var(--color-label-literature);
}

.detail-row--oup {
  border-left-color: var(--color-label-oup);
}

.detail-row--arbitration {
  border-left-color: var(--color-label-arbitration);
}

.detail-row--jurisdiction {
  border-left-color: var(--color-cold-purple);
}

.label-key {
  padding: 0;
}

.label-key span {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-weight: 500;
  font-size: 0.75rem;
  color: var(--color-cold-night-alpha);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

/* InfoPopover icon styling */
.label-key :deep(svg) {
  color: var(--color-cold-night-alpha-25);
  transition: color 0.2s ease;
}

.label-key:hover :deep(svg) {
  color: var(--color-cold-night-alpha);
}
</style>
