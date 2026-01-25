<template>
  <div class="mt-8 mb-4 space-y-5" role="status" aria-label="Loading">
    <div class="loading-skeleton w-[260px]" />
    <div class="loading-skeleton w-[330px]" />
    <div class="loading-skeleton w-[300px]" />
    <div class="loading-skeleton w-[280px]" />
    <span class="sr-only">Loading content</span>
  </div>
</template>

<style scoped>
.loading-skeleton {
  height: 16px;
  border-radius: 4px;
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-purple) 8%, white),
    color-mix(in srgb, var(--color-cold-green) 6%, white)
  );
  position: relative;
  overflow: hidden;
}

.loading-skeleton::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    color-mix(in srgb, var(--color-cold-purple) 12%, white) 50%,
    transparent 100%
  );
  animation: shimmer 1.8s ease-in-out infinite;
  transform: translateX(-100%);
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@media (prefers-reduced-motion: reduce) {
  .loading-skeleton::after {
    animation: none;
    transform: none;
    background: color-mix(in srgb, var(--color-cold-purple) 4%, transparent);
  }
}
</style>
