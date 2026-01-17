<template>
  <div v-if="shouldShowSection">
    <div v-if="isLoading">
      <LoadingBar />
    </div>
    <div v-else-if="displayedItems.length" class="result-value-small">
      <div class="mb-2 flex flex-row flex-wrap gap-x-6 gap-y-2">
        <NuxtLink
          v-for="item in displayedItems"
          :key="item.id"
          class="link-chip--neutral"
          :to="item.id.startsWith('/') ? item.id : `${basePath}/${item.id}`"
        >
          {{ item.title }}
        </NuxtLink>
        <button
          v-if="items.length > 10"
          class="link-chip--action"
          @click="showAll = !showAll"
        >
          {{ showAll ? "Show less" : "Show more" }}
        </button>
      </div>
    </div>
    <p
      v-else-if="emptyValueBehavior.action === 'display'"
      class="result-value-small"
    >
      —
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import type { RelatedItem, EmptyValueBehavior } from "@/types/ui";

const props = withDefaults(
  defineProps<{
    items?: RelatedItem[];
    isLoading?: boolean;
    basePath: string;
    emptyValueBehavior?: EmptyValueBehavior;
  }>(),
  {
    items: () => [],
    isLoading: false,
    emptyValueBehavior: () => ({
      action: "display",
      fallback: "No items available",
    }),
  },
);

const showAll = ref(false);

const hasItems = computed(() => props.items.length > 0);

const shouldShowSection = computed(
  () =>
    props.isLoading ||
    hasItems.value ||
    (!hasItems.value && props.emptyValueBehavior.action === "display"),
);

const displayedItems = computed(() => {
  return !showAll.value && props.items.length > 10
    ? props.items.slice(0, 10)
    : props.items;
});
</script>
