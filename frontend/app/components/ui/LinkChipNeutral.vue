<template>
  <a class="link-chip--neutral" v-bind="$attrs">
    <slot />
  </a>
</template>

<script setup lang="ts">
defineOptions({ inheritAttrs: false });
</script>

<style>
@reference "@/assets/styles.css";

.link-chip--neutral {
  @apply -ml-3 inline-flex items-center rounded-lg px-3 py-1.5 text-sm font-medium text-pretty;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  transition:
    background 150ms,
    box-shadow 150ms,
    margin-right 0.2s ease;
  background: var(--gradient-subtle);
  color: var(--color-cold-night);
}

.link-chip--neutral:hover {
  box-shadow:
    0 1px 3px 0 rgb(0 0 0 / 0.1),
    0 1px 2px -1px rgb(0 0 0 / 0.1);
  background: var(--gradient-subtle-emphasis);
  margin-right: -1rem;
  color: var(--color-cold-purple);
}

.link-chip--neutral::after {
  content: "";
  display: inline-block;
  width: 0;
  height: 12px;
  margin-left: 0;
  background-color: currentColor;
  mask-image: var(--icon-arrow-right);
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  -webkit-mask-image: var(--icon-arrow-right);
  -webkit-mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  opacity: 0;
  transition:
    width 0.2s ease,
    margin-left 0.2s ease,
    opacity 0.15s ease;
}

.link-chip--neutral:hover::after {
  width: 1rem;
  opacity: 1;
}

.link-chip--neutral:focus-visible {
  @apply outline-2 outline-offset-2;
  outline-color: var(--color-cold-purple);
}

.link-chip--neutral > span {
  overflow: visible;
  white-space: normal;
  text-overflow: unset;
}
</style>
