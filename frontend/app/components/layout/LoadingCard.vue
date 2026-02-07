<template>
  <ResultCard card-type="Loading" :result-data="{}">
    <div class="mt-4 mb-3 space-y-3" role="status" aria-label="Loading">
      <div class="loading-skeleton loading-skeleton--sm w-[40px]" />
      <div class="loading-skeleton w-[310px]" />
      <div class="loading-skeleton w-[280px]" />
      <span class="sr-only">Loading content</span>
    </div>
  </ResultCard>
</template>

<script setup lang="ts">
import ResultCard from "@/components/search-results/ResultCard.vue";
</script>

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

.loading-skeleton--sm {
  height: 12px;
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
