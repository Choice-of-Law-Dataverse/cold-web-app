<template>
  <NuxtLink :to="buttonLink" class="block h-full">
    <UCard ref="cardRef" class="number-card h-full">
      <div class="flex h-full flex-col justify-between">
        <h2 class="card-title mb-4 text-center">
          {{ title }}
        </h2>
        <div class="number-container">
          <span v-if="!loading && !error" class="number-display">
            {{ displayNumber }}
          </span>
          <span v-else-if="loading">
            <span
              class="flex items-center justify-center"
              role="status"
              aria-live="polite"
              aria-label="Loading"
            >
              <span class="loading-digits">
                <span class="digit" style="animation-delay: 0ms">0</span>
                <span class="digit" style="animation-delay: 100ms">0</span>
                <span class="digit" style="animation-delay: 200ms">0</span>
              </span>
              <span class="sr-only">Loading content</span>
            </span>
          </span>
          <span v-else>Error</span>
        </div>
      </div>
    </UCard>
  </NuxtLink>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from "vue";
import { useNumberCount } from "~/composables/useNumberCount";
import type { TableName } from "@/types/api";

const props = defineProps<{
  title: string;
  buttonText: string;
  buttonLink: string;
  tableName: TableName;
  overrideNumber?: number | string | null;
}>();

const {
  data: number,
  isLoading: loading,
  error,
} = useNumberCount(
  computed(() =>
    props.overrideNumber
      ? (undefined as unknown as TableName)
      : props.tableName,
  ),
);

const displayNumber = ref(0);
const cardRef = ref<{ $el?: HTMLElement } | null>(null);
const hasAnimated = ref(false);

function animateCount(target: number) {
  if (hasAnimated.value) {
    displayNumber.value = target;
    return;
  }
  hasAnimated.value = true;
  const duration = 1200;
  const start = performance.now();
  const from = 0;

  function step(now: number) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    displayNumber.value = Math.round(from + (target - from) * eased);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

const targetValue = computed(() => {
  const raw = number.value ?? props.overrideNumber;
  if (raw == null) return 0;
  return typeof raw === "string" ? parseInt(raw, 10) || 0 : raw;
});

let observer: IntersectionObserver | null = null;

onMounted(() => {
  const prefersReduced = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;
  if (prefersReduced) {
    hasAnimated.value = true;
    watch(
      targetValue,
      (v) => {
        displayNumber.value = v;
      },
      { immediate: true },
    );
    return;
  }

  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0]?.isIntersecting && targetValue.value > 0) {
        animateCount(targetValue.value);
        observer?.disconnect();
      }
    },
    { threshold: 0.3 },
  );
  const el = cardRef.value?.$el;
  if (el) observer.observe(el);

  watch(targetValue, (v) => {
    if (hasAnimated.value) {
      displayNumber.value = v;
    } else if (cardRef.value?.$el && observer) {
      observer.disconnect();
      observer.observe(cardRef.value.$el);
    }
  });
});

onUnmounted(() => {
  observer?.disconnect();
});
</script>

<style scoped>
@reference "tailwindcss";

.number-card {
  @apply transition-all duration-200;
}

a:hover .number-card {
  @apply shadow-md;
  transform: translateY(-1px);
}

.card-title {
  line-height: 1.4;
  height: 3.6em;
  display: flex;
  align-items: center;
  justify-content: center;
}

.number-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
  flex: 1;
}

.number-display {
  font-size: clamp(2.5rem, 8vw, 4rem);
  font-weight: 700;
  background: linear-gradient(
    135deg,
    var(--color-cold-purple),
    var(--color-cold-green)
  );
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  cursor: pointer;
  transition: filter 0.2s ease;
  font-variant-numeric: tabular-nums;
}

a:hover .number-display {
  filter: brightness(0.85);
}

.loading-digits {
  display: flex;
  gap: 2px;
}

.digit {
  font-size: clamp(2.5rem, 8vw, 4rem);
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
