<template>
  <div
    class="flex items-center justify-center"
    role="status"
    aria-live="polite"
    aria-label="Loading"
  >
    <div class="loading-number">
      <div class="loading-digits">
        <span class="digit" style="animation-delay: 0ms">0</span>
        <span class="digit" style="animation-delay: 100ms">0</span>
        <span class="digit" style="animation-delay: 200ms">0</span>
      </div>
    </div>
    <span class="sr-only">Loading content</span>
  </div>
</template>

<style scoped>
.loading-number {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-digits {
  display: flex;
  gap: 2px;
}

.digit {
  font-size: 64px;
  font-weight: 700;
  background: linear-gradient(
    135deg,
    var(--color-cold-purple),
    var(--color-cold-green)
  );
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  opacity: 0.3;
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.6;
  }
}

@media (prefers-reduced-motion: reduce) {
  .digit {
    animation: none;
    opacity: 0.5;
  }
}
</style>
