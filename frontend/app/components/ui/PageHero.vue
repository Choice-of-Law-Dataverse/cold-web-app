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
            <svg class="sparkle-icon" viewBox="0 0 24 24" fill="currentColor">
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
