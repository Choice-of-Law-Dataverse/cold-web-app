<template>
  <div class="moderation-hub py-12">
    <div class="mb-10">
      <h1 class="text-cold-night text-2xl font-bold tracking-tight sm:text-3xl">
        Moderation Queue
      </h1>
      <p class="text-cold-slate mt-2 text-sm">
        Review and action pending submissions across all categories.
      </p>
    </div>

    <div v-if="pending" class="flex justify-center py-16">
      <UIcon name="i-heroicons-arrow-path" class="h-8 w-8 animate-spin" />
    </div>

    <template v-else>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink
          v-for="cat in categoriesWithCounts"
          :key="cat.id"
          :to="
            cat.id === 'feedback'
              ? '/moderation/feedback'
              : `/moderation/${cat.id}`
          "
          class="category-card group"
          :style="{ '--cat-color': cat.color }"
        >
          <div class="card-inner">
            <div class="flex items-center gap-3">
              <div
                class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg"
                :style="{
                  background: `color-mix(in srgb, ${cat.color} 12%, white)`,
                }"
              >
                <UIcon
                  :name="cat.icon"
                  class="h-[18px] w-[18px]"
                  :style="{ color: cat.color }"
                />
              </div>
              <div class="min-w-0 flex-1">
                <h2
                  class="text-cold-night text-[15px] leading-tight font-semibold"
                >
                  {{ cat.label }}
                </h2>
              </div>
              <span
                class="count-badge"
                :class="cat.pendingCount > 0 ? '' : 'count-badge--zero'"
                :style="
                  cat.pendingCount > 0 ? { background: cat.color } : undefined
                "
              >
                {{ cat.pendingCount }}
              </span>
            </div>

            <div class="mt-3 flex items-center justify-between">
              <p
                class="text-[13px]"
                :class="
                  cat.pendingCount > 0
                    ? 'text-cold-night font-medium'
                    : 'text-cold-slate'
                "
              >
                <template v-if="cat.pendingCount > 0">
                  {{ cat.pendingCount }}
                  {{ cat.pendingCount === 1 ? "item" : "items" }} pending
                </template>
                <template v-else> All clear </template>
              </p>
              <UIcon
                name="i-heroicons-chevron-right-16-solid"
                class="text-cold-slate h-4 w-4 transition-all group-hover:translate-x-0.5"
                :style="{ color: cat.pendingCount > 0 ? cat.color : undefined }"
              />
            </div>
          </div>
        </NuxtLink>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import {
  MODERATION_CATEGORIES,
  type CategoryConfig,
} from "@/config/moderationConfig";
import { useModerationApi } from "@/composables/useModerationApi";
import type { ModerationSummaryItem } from "@/composables/useModerationApi";

definePageMeta({
  middleware: ["moderation"],
});

const { getModerationSummary } = useModerationApi();

const { data: summary, pending } = await useAsyncData(
  "moderation-summary",
  () => getModerationSummary(),
  { server: false },
);

interface CategoryWithCount extends CategoryConfig {
  pendingCount: number;
}

const categoriesWithCounts = computed((): CategoryWithCount[] => {
  const countMap = new Map<string, number>();
  if (summary.value) {
    summary.value.forEach((item: ModerationSummaryItem) => {
      countMap.set(item.category, item.pendingCount);
    });
  }
  return MODERATION_CATEGORIES.map((cat) => ({
    ...cat,
    pendingCount: countMap.get(cat.id) ?? 0,
  }));
});
</script>

<style scoped>
.moderation-hub h1,
.moderation-hub h2 {
  font-family: "DM Sans", sans-serif;
}

.category-card {
  display: block;
  border-radius: 12px;
  border: 1px solid var(--color-cold-gray);
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.category-card:hover {
  border-color: color-mix(in srgb, var(--cat-color) 40%, transparent);
  box-shadow: 0 4px 24px color-mix(in srgb, var(--cat-color) 8%, transparent);
}

.card-inner {
  padding: 1rem 1.25rem;
  background: white;
  border-radius: 11px;
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2rem;
  height: 2rem;
  padding: 0 0.5rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 700;
  color: white;
}

.count-badge--zero {
  background: var(--color-cold-gray);
  color: var(--color-cold-slate);
  font-weight: 500;
}
</style>
