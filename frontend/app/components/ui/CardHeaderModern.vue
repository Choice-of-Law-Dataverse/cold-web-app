<template>
  <div class="card-header-modern">
    <div v-if="$slots.icon" class="card-header-modern__icon">
      <slot name="icon" />
    </div>
    <div class="card-header-modern__text">
      <slot />
    </div>
  </div>
</template>

<style>
@reference "tailwindcss";

.card-header-modern {
  @apply flex items-center gap-3;
}

.card-header-modern__icon {
  @apply flex h-10 w-10 items-center justify-center rounded-xl;
  background-image: linear-gradient(
    to bottom right,
    var(--color-cold-teal),
    var(--color-cold-green)
  );
}

.card-header-modern__text h3 {
  @apply font-semibold text-gray-900;
}

.card-header-modern__text p {
  @apply text-xs text-gray-500;
}
</style>
