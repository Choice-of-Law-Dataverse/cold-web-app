<template>
  <UButton
    v-bind="$attrs"
    :icon="icon"
    :label="label"
    :disabled="disabled"
    :aria-disabled="disabled || undefined"
    :aria-pressed="pressed"
    class="cold-control-shell"
    :class="pressed === true ? 'cold-control-shell--pressed' : ''"
  >
    <slot />
  </UButton>
</template>

<script setup lang="ts">
defineOptions({ inheritAttrs: false });

withDefaults(
  defineProps<{
    icon?: string;
    label?: string;
    disabled?: boolean;
    pressed?: boolean;
  }>(),
  {
    icon: undefined,
    label: undefined,
    disabled: false,
    pressed: undefined,
  },
);
</script>

<style>
.cold-control-shell {
  @apply inline-flex w-full items-center rounded-lg px-3 font-medium;
  height: 42px;
  border: 1px solid rgb(229 231 235);
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  background: var(--gradient-subtle);
  color: var(--color-cold-purple);
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease,
    background 0.15s ease,
    color 0.15s ease,
    transform 0.15s ease;
}

.cold-control-shell:hover {
  border-color: rgb(209 213 219);
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  background: var(--gradient-subtle-hover);
}

.cold-control-shell:focus,
.cold-control-shell:focus-visible {
  outline: 2px solid var(--color-cold-purple);
  outline-offset: 2px;
  border-color: var(--color-cold-purple);
}

.cold-control-shell[disabled],
.cold-control-shell:disabled,
.cold-control-shell[aria-disabled="true"] {
  background-color: var(--color-cold-gray-alpha);
  color: var(--color-cold-night-alpha);
  cursor: not-allowed;
}

.cold-control-shell--pressed,
.cold-control-shell[aria-pressed="true"] {
  border-color: var(--color-cold-purple);
  background: var(--gradient-medium-hover);
  font-weight: 600;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}
</style>
