<template>
  <div v-if="shouldShowSection">
    <div v-if="isLoading">
      <LoadingBar />
    </div>
    <div v-else-if="displayedItems.length" class="result-value-small">
      <div class="mb-2 flex flex-row flex-wrap gap-2">
        <NuxtLink
          v-for="item in displayedItems"
          :key="item.id"
          :class="[
            'inline-flex items-center rounded-full px-3 py-1 text-sm text-pretty shadow-sm transition-all',
            badgeColorClass,
          ]"
          :to="item.id.startsWith('/') ? item.id : `${basePath}/${item.id}`"
        >
          {{ item.title }}
        </NuxtLink>
        <button
          v-if="fullItemsList.length > 10"
          class="bg-cold-teal/10 text-cold-teal hover:bg-cold-teal/20 inline-flex items-center rounded-full px-3 py-1 text-sm shadow-sm transition-colors hover:shadow-md"
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

const badgeColorClass = computed(() => {
  const type = props.entityType.toLowerCase();

  if (type.includes("court") || type.includes("decision")) {
    return "bg-label-court-decision/10 text-cold-night hover:bg-label-court-decision/20 hover:shadow-md";
  }
  if (type.includes("question") || type.includes("answer")) {
    return "bg-label-question/10 text-cold-night hover:bg-label-question/20 hover:shadow-md";
  }
  if (type.includes("instrument")) {
    return "bg-label-instrument/10 text-cold-night hover:bg-label-instrument/20 hover:shadow-md";
  }
  if (type.includes("literature")) {
    return "bg-label-literature/10 text-cold-night hover:bg-label-literature/20 hover:shadow-md";
  }
  if (type.includes("arbitr")) {
    return "bg-label-arbitration/10 text-cold-night hover:bg-label-arbitration/20 hover:shadow-md";
  }
  if (type.includes("oup-chapter")) {
    return "bg-blue-900/10 text-cold-night hover:bg-blue-900/20 hover:shadow-md";
  }

  // Default fallback
  return "bg-cold-purple/10 text-cold-night hover:bg-cold-purple/20 hover:shadow-md";
});
</script>

<style scoped>
a {
  color: var(--color-cold-night);
}
</style>
