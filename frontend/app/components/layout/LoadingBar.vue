<template>
  <div class="mb-2.5 space-y-2">
    <div
      class="loading-bar"
      role="status"
      aria-label="Loading"
      :style="{ width: randomWidth }"
    >
      <div class="loading-bar__shimmer" />
    </div>
    <span class="sr-only">Loading content</span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";

const randomWidth = ref("280px");

onMounted(() => {
  randomWidth.value = `${Math.floor(Math.random() * (350 - 200 + 1)) + 200}px`;
});
</script>

<style scoped>
.loading-bar {
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-purple) 8%, white),
    color-mix(in srgb, var(--color-cold-green) 6%, white)
  );
  position: relative;
  overflow: hidden;
}

.loading-bar__shimmer {
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
  .loading-bar__shimmer {
    animation: none;
    transform: none;
    background: color-mix(in srgb, var(--color-cold-purple) 4%, transparent);
  }
}
</style>
