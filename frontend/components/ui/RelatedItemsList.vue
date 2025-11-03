<template>
  <div v-if="shouldShowSection">
    <div v-if="isLoading">
      <LoadingBar />
    </div>
    <div
      v-else-if="displayedItems.length"
      class="result-value-small flex flex-col gap-1"
    >
      <div v-for="item in displayedItems" :key="item.id">
        <NuxtLink :to="`${basePath}/${item.id}`">
          {{ item.title }}
        </NuxtLink>
      </div>
      <ShowMoreLess
        v-if="fullItemsList.length > 5"
        v-model:is-expanded="showAll"
      />
    </div>
    <p v-else-if="emptyValueBehavior.action === 'display'" class="prose">
      {{ emptyValueBehavior.fallback }}
    </p>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import ShowMoreLess from "@/components/ui/ShowMoreLess.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";

const props = defineProps({
  items: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false },
  basePath: { type: String, required: true },
  emptyValueBehavior: {
    type: Object,
    default: () => ({
      action: "display",
      fallback: "No items available",
    }),
  },
});

const showAll = ref(false);

const fullItemsList = computed(() => props.items || []);

const hasItems = computed(() => fullItemsList.value.length > 0);

const shouldShowSection = computed(
  () =>
    props.isLoading ||
    hasItems.value ||
    (!hasItems.value && props.emptyValueBehavior.action === "display"),
);

const displayedItems = computed(() => {
  const arr = fullItemsList.value;
  return !showAll.value && arr.length >= 5 ? arr.slice(0, 5) : arr;
});
</script>
