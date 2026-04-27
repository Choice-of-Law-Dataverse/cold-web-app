<template>
  <component
    :is="rootTag"
    ref="rootRef"
    :type="asButton ? 'button' : undefined"
    :to="!asButton && to ? to : undefined"
    :style="{ '--schip-color': tone }"
    :class="[
      'schip',
      isStatic && 'schip--static',
      asButton && 'schip--button',
      compact && 'schip--compact',
    ]"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed, ref, resolveComponent } from "vue";

const props = withDefaults(
  defineProps<{
    to?: string;
    asButton?: boolean;
    isStatic?: boolean;
    compact?: boolean;
    tone?: string;
  }>(),
  {
    to: "",
    asButton: false,
    isStatic: false,
    compact: false,
    tone: "var(--color-cold-purple)",
  },
);

const rootTag = computed(() => {
  if (props.asButton) return "button";
  if (props.to) return resolveComponent("NuxtLink");
  return "span";
});

const rootRef = ref<HTMLElement | { $el: HTMLElement } | null>(null);

const rootEl = computed<HTMLElement | null>(() => {
  const r = rootRef.value;
  if (!r) return null;
  if (r instanceof HTMLElement) return r;
  return r.$el ?? null;
});

defineExpose({ rootEl });
</script>

<style>
@reference "tailwindcss";

.schip {
  --schip-pad-x: 9px;
  --schip-pad-y: 2px;
  --schip-gap: 5px;
  --schip-font-size: 11px;
  --schip-icon-size: 11px;
  --schip-flag-w: 16px;
  --schip-flag-h: 11px;

  @apply inline-flex items-center rounded-full border border-transparent font-mono font-semibold tracking-wider whitespace-nowrap uppercase no-underline transition-[background,border-color,color] duration-150;
  gap: var(--schip-gap);
  padding: var(--schip-pad-y) var(--schip-pad-x);
  font-size: var(--schip-font-size);
  background: color-mix(in srgb, var(--schip-color) 8%, white);
  color: color-mix(in srgb, var(--schip-color) 80%, black);
}

.schip--compact {
  --schip-pad-x: 7px;
  --schip-pad-y: 1px;
  --schip-gap: 4px;
  --schip-font-size: 10px;
  --schip-icon-size: 10px;
  --schip-flag-w: 14px;
  --schip-flag-h: 10px;

  letter-spacing: 0.04em;
}

.schip:not(.schip--static):hover {
  background: color-mix(in srgb, var(--schip-color) 14%, white);
  border-color: color-mix(in srgb, var(--schip-color) 30%, white);
  color: color-mix(in srgb, var(--schip-color) 95%, black);
}

.schip--static {
  @apply cursor-default;
}

.schip--button {
  @apply m-0 cursor-pointer appearance-none;
}

.schip-flag-wrap,
.schip-arrow-wrap {
  @apply inline-flex flex-shrink-0 items-center justify-center overflow-hidden transition-[width,opacity] duration-150;
  width: var(--schip-flag-w);
  height: var(--schip-flag-h);
}

.schip-flag {
  @apply object-contain;
  width: var(--schip-flag-w);
  height: var(--schip-flag-h);
}

.schip-arrow-wrap {
  @apply opacity-0;
  width: 0;
  font-size: 12px;
}

.schip--compact .schip-arrow-wrap {
  font-size: var(--schip-icon-size);
}

.schip:not(.schip--static):hover .schip-flag-wrap {
  @apply opacity-0;
  width: 0;
}

.schip:not(.schip--static):hover .schip-arrow-wrap {
  @apply opacity-90;
  width: var(--schip-flag-w);
}

.schip-tag,
.schip-affordance {
  @apply inline-flex flex-shrink-0 items-center justify-center overflow-hidden transition-[width,opacity] duration-150;
  width: var(--schip-icon-size);
  font-size: var(--schip-icon-size);
}

.schip-tag {
  @apply opacity-65;
}

.schip-affordance {
  @apply opacity-0;
  width: 0;
}

.schip:not(.schip--static):hover .schip-tag {
  @apply opacity-0;
  width: 0;
}

.schip:not(.schip--static):hover .schip-affordance {
  @apply opacity-90;
  width: var(--schip-icon-size);
}
</style>
