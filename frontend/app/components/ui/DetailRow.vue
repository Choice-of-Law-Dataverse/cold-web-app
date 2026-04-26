<template>
  <div class="detail-row @container" :class="variant ? `type-${variant}` : ''">
    <div class="flex flex-col gap-2 @md:flex-row @md:items-start @md:gap-10">
      <div class="label-key flex flex-col items-start @md:w-48 @md:shrink-0">
        <span class="flex items-center gap-1.5">
          <span class="mono-font">
            {{ label }}
          </span>
          <slot name="label-actions" />
          <InfoPopover v-if="tooltip" :text="tooltip" />
        </span>
        <div v-if="$slots['label-subtitle']" class="label-subtitle">
          <slot name="label-subtitle" />
        </div>
      </div>

      <div class="detail-value w-full @md:flex-1">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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
    validator: (value: string) =>
      [
        "court-decision",
        "question",
        "instrument",
        "literature",
        "oup",
        "arbitration",
        "jurisdiction",
        "specialist",
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
  background: var(--gradient-row-hover);
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

.label-key :deep(svg) {
  color: var(--color-cold-night-alpha-25);
  transition: color 0.2s ease;
}

.label-key:hover :deep(svg) {
  color: var(--color-cold-night-alpha);
}

.label-subtitle {
  display: block;
  margin-top: 0.125rem;
  font-size: 0.7rem;
  font-weight: 400;
  color: var(--color-cold-night-alpha);
  text-transform: none;
  letter-spacing: normal;
  opacity: 0.6;
}
</style>
