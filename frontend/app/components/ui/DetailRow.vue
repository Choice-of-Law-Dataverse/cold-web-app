<template>
  <div
    class="detail-row flex flex-col gap-3 md:flex-row md:items-start md:gap-10"
    :class="variant ? `type-${variant}` : ''"
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

    <div class="detail-value w-full md:flex-1">
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
  position: relative;
  padding: 0.75rem 1rem;
  margin: 0 -1rem;
  border-radius: 2px;
  transition: background 0.15s ease;

  @media (min-width: 640px) {
    padding: 0.75rem 1.5rem;
    margin: 0 -1.5rem;
  }
}

.detail-row::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 2px;
  background: color-mix(
    in srgb,
    var(--type-color, transparent) 50%,
    transparent
  );
}

.detail-row:hover {
  background: linear-gradient(
    315deg,
    color-mix(in srgb, var(--color-cold-purple) 2%, white),
    color-mix(in srgb, var(--color-cold-green) 1%, white)
  );
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
