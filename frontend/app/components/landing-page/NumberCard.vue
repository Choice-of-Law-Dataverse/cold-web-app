<template>
  <NuxtLink ref="cardRef" :to="buttonLink" class="stat-card">
    <span v-if="!loading && !error" class="stat-number">
      {{ formatted }}
    </span>
    <span
      v-else-if="loading"
      class="stat-number stat-number--loading"
      role="status"
      aria-live="polite"
      aria-label="Loading count"
    >
      <span class="dot" />
      <span class="dot" />
      <span class="dot" />
    </span>
    <span v-else class="stat-number stat-number--error">—</span>

    <span class="stat-divider" aria-hidden="true" />

    <span class="stat-label">{{ title }}</span>

    <Icon
      name="i-material-symbols:arrow-forward-rounded"
      class="stat-arrow"
      aria-hidden="true"
    />
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

const formatted = computed(() => displayNumber.value.toLocaleString("en-US"));

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
.stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: #ffffff;
  border: 1px solid color-mix(in srgb, var(--color-cold-night) 8%, transparent);
  border-radius: 0.75rem;
  text-decoration: none;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
  min-height: 60px;
  isolation: isolate;
}

.stat-card:hover {
  border-color: color-mix(in srgb, var(--color-cold-purple) 30%, transparent);
  box-shadow: 0 6px 18px -10px
    color-mix(in srgb, var(--color-cold-purple) 35%, transparent);
  transform: translateY(-1px);
}

.stat-number {
  font-family: "DM Sans", sans-serif;
  font-size: clamp(1.625rem, 2.4vw, 2rem);
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.02em;
  background: linear-gradient(
    135deg,
    var(--color-cold-purple),
    var(--color-cold-green)
  );
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
  min-width: 2.5ch;
  display: inline-flex;
  align-items: center;
}

.stat-number--error {
  -webkit-text-fill-color: var(--color-cold-slate);
  color: var(--color-cold-slate);
  background: none;
}

.stat-divider {
  width: 1px;
  align-self: stretch;
  background: color-mix(in srgb, var(--color-cold-night) 10%, transparent);
  flex-shrink: 0;
  margin-block: 0.25rem;
}

.stat-label {
  flex: 1 1 auto;
  font-family: "DM Sans", sans-serif;
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.25;
  color: var(--color-cold-night);
  letter-spacing: 0.005em;
}

.stat-arrow {
  font-size: 1rem;
  color: color-mix(in srgb, var(--color-cold-night) 45%, transparent);
  transition:
    transform 0.2s ease,
    color 0.2s ease;
  flex-shrink: 0;
}

.stat-card:hover .stat-arrow {
  color: var(--color-cold-purple);
  transform: translateX(3px);
}

.stat-number--loading {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: clamp(1.625rem, 2.4vw, 2rem);
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background: linear-gradient(
    135deg,
    var(--color-cold-purple),
    var(--color-cold-green)
  );
  opacity: 0.4;
  animation: stat-pulse 1.2s ease-in-out infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.15s;
}

.dot:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes stat-pulse {
  0%,
  100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .dot {
    animation: none;
    opacity: 0.5;
  }
  .stat-card:hover {
    transform: none;
  }
  .stat-card:hover .stat-arrow {
    transform: none;
  }
}

@media (max-width: 480px) {
  .stat-card {
    padding: 0.75rem 0.875rem;
    gap: 0.625rem;
    min-height: 56px;
  }
  .stat-divider {
    display: none;
  }
  .stat-label {
    font-size: 0.75rem;
  }
}
</style>
