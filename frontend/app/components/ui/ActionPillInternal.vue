<template>
  <button type="button" class="action-pill-internal" v-bind="$attrs">
    <slot />
  </button>
</template>

<style>
@reference "tailwindcss";

.action-pill-internal {
  @apply inline-flex cursor-pointer items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium uppercase transition-colors duration-150;
  color: var(--color-cold-night);
  background: white;
  border: 1.5px solid
    color-mix(in srgb, var(--color-cold-night) 25%, transparent);
}

.action-pill-internal:hover {
  background: var(--color-cold-night);
  color: white;
  border-color: var(--color-cold-night);
}

.action-pill-internal:focus-visible {
  @apply outline-2 outline-offset-2;
  outline-color: var(--color-cold-purple);
}

.action-pill-internal svg,
.action-pill-internal .iconify {
  font-size: 1.1em;
  @apply transition-transform duration-150;
}

.action-pill-internal:hover svg,
.action-pill-internal:hover .iconify {
  @apply scale-105;
}
</style>
