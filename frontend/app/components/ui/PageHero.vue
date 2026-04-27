<template>
  <div class="page-hero">
    <!-- Decorative background orbs -->
    <div class="page-hero__bg">
      <div class="page-hero__orb page-hero__orb--left" />
      <div class="page-hero__orb page-hero__orb--right" />
    </div>

    <div class="page-hero__content">
      <div class="flex-1">
        <!-- Optional badge -->
        <div v-if="badge" class="page-hero__badge">
          <slot name="badge-icon">
            <svg class="h-3 w-3" viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M12 2L13.09 8.26L19 9L13.09 9.74L12 16L10.91 9.74L5 9L10.91 8.26L12 2Z"
              />
            </svg>
          </slot>
          {{ badge }}
        </div>

        <!-- Title -->
        <h1 class="page-hero__title">
          <slot name="title">{{ title }}</slot>
        </h1>

        <!-- Subtitle -->
        <p v-if="subtitle || $slots.subtitle" class="page-hero__subtitle">
          <slot name="subtitle">{{ subtitle }}</slot>
        </p>

        <!-- Extra content slot -->
        <slot name="content" />
      </div>

      <!-- Illustration slot -->
      <div v-if="$slots.illustration" class="hidden md:block">
        <slot name="illustration" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
  subtitle?: string;
  badge?: string;
}>();
</script>

<style>
@reference "tailwindcss";

.page-hero {
  @apply relative mb-10 overflow-hidden rounded-2xl p-6 sm:p-8;
  background-image: linear-gradient(
    to bottom right,
    color-mix(in srgb, var(--color-cold-purple) 5%, white),
    white,
    color-mix(in srgb, var(--color-cold-teal) 5%, white)
  );
}

.page-hero__bg {
  @apply pointer-events-none absolute inset-0 overflow-hidden;
}

.page-hero__orb {
  @apply absolute rounded-full blur-[48px];
}

.page-hero__orb--left {
  @apply -top-20 -left-20 h-64 w-64;
  background-image: linear-gradient(
    to bottom right,
    color-mix(in srgb, var(--color-cold-purple) 10%, transparent),
    transparent
  );
}

.page-hero__orb--right {
  @apply -right-20 -bottom-20 h-64 w-64;
  background-image: linear-gradient(
    to top left,
    color-mix(in srgb, var(--color-cold-teal) 10%, transparent),
    transparent
  );
}

.page-hero__content {
  @apply relative flex items-center gap-6 sm:gap-8;
}

.page-hero__badge {
  @apply mb-3 inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold text-white;
  background-image: linear-gradient(
    to right,
    var(--color-cold-purple),
    var(--color-cold-teal)
  );
}

.page-hero__title {
  @apply bg-clip-text text-3xl font-bold text-transparent sm:text-4xl;
  background-image: linear-gradient(
    to right,
    var(--color-cold-night),
    var(--color-cold-purple)
  );
  -webkit-background-clip: text;
}

.page-hero__subtitle {
  @apply mt-3 max-w-lg text-base text-gray-600;
}
</style>
