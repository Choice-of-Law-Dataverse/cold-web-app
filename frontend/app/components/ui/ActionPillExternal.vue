<template>
  <a
    target="_blank"
    rel="noopener noreferrer"
    class="action-pill-external"
    v-bind="$attrs"
  >
    <slot />
  </a>
</template>

<style>
@reference "tailwindcss";

.action-pill-external {
  @apply inline-flex cursor-pointer items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium uppercase transition-colors duration-150;
  color: var(--color-cold-teal);
  background: color-mix(in srgb, var(--color-cold-teal) 6%, white);
  border: 1px solid color-mix(in srgb, var(--color-cold-teal) 20%, transparent);
}

.action-pill-external:hover {
  background: color-mix(in srgb, var(--color-cold-teal) 12%, white);
  border-color: color-mix(in srgb, var(--color-cold-teal) 35%, transparent);
  @apply shadow-sm;
}

.action-pill-external:focus-visible {
  @apply outline-2 outline-offset-2;
  outline-color: var(--color-cold-teal);
}

.action-pill-external svg,
.action-pill-external .iconify {
  font-size: 1.1em;
  @apply transition-transform duration-150;
}

.action-pill-external:hover svg,
.action-pill-external:hover .iconify {
  @apply scale-105;
}
</style>
