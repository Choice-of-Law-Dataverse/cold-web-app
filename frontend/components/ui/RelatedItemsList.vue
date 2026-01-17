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
          :class="chipClass"
          :to="item.id.startsWith('/') ? item.id : `${basePath}/${item.id}`"
        >
          {{ item.title }}
        </NuxtLink>
        <button
          v-if="fullItemsList.length > 10"
          class="link-chip--action"
          @click="showAll = !showAll"
        >
          {{ showAll ? "Show less" : "Show more" }}
        </button>
      </div>
    </div>
    <p v-else-if="emptyValueBehavior.action === 'display'" class="prose">
      {{ emptyValueBehavior.fallback }}
    </p>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";

const props = defineProps({
  items: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false },
  basePath: { type: String, required: true },
  entityType: { type: String, default: "" },
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
  return !showAll.value && arr.length > 10 ? arr.slice(0, 10) : arr;
});

// Use neutral chip style - semantic color is on the DetailRow label
const chipClass = "link-chip--neutral";
</script>
