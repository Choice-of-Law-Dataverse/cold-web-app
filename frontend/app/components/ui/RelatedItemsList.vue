<template>
  <div v-if="shouldShowSection">
    <div v-if="isLoading">
      <LoadingBar />
    </div>
    <InlineError v-else-if="error" :error="error" />
    <div v-else-if="displayedItems.length" class="result-value-small">
      <div class="mb-2 flex flex-row flex-wrap gap-x-6 gap-y-2">
        <UButton
          v-for="item in displayedItems"
          :key="item.id"
          variant="ghost"
          color="neutral"
          class="link-chip--neutral"
          trailing-icon="i-material-symbols:arrow-forward"
          :to="item.id.startsWith('/') ? item.id : `${basePath}/${item.id}`"
        >
          {{ item.title }}
        </UButton>
      </div>
      <ShowMoreLess
        v-if="items.length > 10"
        v-model:is-expanded="showAll"
        button-class="link-chip--action"
      />
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
import InlineError from "@/components/ui/InlineError.vue";
import ShowMoreLess from "@/components/ui/ShowMoreLess.vue";
import type { RelatedItem, EmptyValueBehavior } from "@/types/ui";

const props = withDefaults(
  defineProps<{
    items?: RelatedItem[];
    isLoading?: boolean;
    error?: Error;
    basePath: string;
    emptyValueBehavior?: EmptyValueBehavior;
  }>(),
  {
    items: () => [],
    isLoading: false,
    error: undefined,
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
