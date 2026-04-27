<template>
  <div class="card-footer-modern">
    <p v-if="$slots.hint" class="card-footer-modern__hint">
      <slot name="hint" />
    </p>
    <div class="card-footer-modern__actions">
      <slot />
    </div>
  </div>
</template>

<style>
@reference "@/assets/styles.css";

.card-footer-modern {
  @apply flex items-center justify-between;
}

.card-footer-modern__hint {
  @apply text-xs text-gray-400;
}

.card-footer-modern__hint .iconify,
.card-footer-modern__hint svg {
  @apply mr-1 inline h-3 w-3;
}

.card-footer-modern__actions {
  @apply flex items-center gap-3;
}
</style>
