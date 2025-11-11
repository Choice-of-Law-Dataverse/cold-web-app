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
            'inline-flex items-center rounded-full px-3 py-1 text-sm transition-colors',
            badgeColorClass,
          ]"
          :style="{ fontWeight: '500' }"
          :to="`${basePath}/${item.id}`"
        >
          {{ item.title }}
        </NuxtLink>
        <button
          v-if="fullItemsList.length > 10"
          class="inline-flex items-center rounded-full bg-cold-teal/5 px-3 py-1 text-sm text-cold-teal transition-colors hover:bg-cold-teal/10"
          :style="{ fontWeight: '500' }"
          @click="showAll = !showAll"
        >
          {{ showAll ? 'Show less' : 'Show more' }}
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
    return "bg-label-court-decision/5 text-label-court-decision hover:bg-label-court-decision/10";
  }
  if (type.includes("question") || type.includes("answer")) {
    return "bg-label-question/5 text-label-question hover:bg-label-question/10";
  }
  if (type.includes("instrument")) {
    return "bg-label-instrument/5 text-label-instrument hover:bg-label-instrument/10";
  }
  if (type.includes("literature")) {
    return "bg-label-literature/5 text-label-literature hover:bg-label-literature/10";
  }
  if (type.includes("arbitr")) {
    return "bg-label-arbitration/5 text-label-arbitration hover:bg-label-arbitration/10";
  }

  // Default fallback
  return "bg-cold-purple/5 text-cold-purple hover:bg-cold-purple/10";
});
</script>
