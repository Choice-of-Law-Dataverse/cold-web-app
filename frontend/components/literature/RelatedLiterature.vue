<template>
  <div v-if="shouldShowSection">
    <div v-if="isLoading">
      <LoadingBar class="ml-[-22px] pt-[11px]" />
    </div>
    <div
      v-else-if="displayedLiterature.length"
      class="result-value-small flex flex-col gap-1"
    >
      <div v-for="item in displayedLiterature" :key="item.id">
        <NuxtLink :to="`/literature/${item.id}`">
          {{ item.title }}
        </NuxtLink>
      </div>
      <ShowMoreLess
        v-if="fullLiteratureList.length > 5"
        v-model:is-expanded="showAll"
      />
    </div>
    <p v-else-if="emptyValueBehavior.action === 'display'">
      {{ emptyValueBehavior.fallback }}
    </p>
  </div>
</template>

<script setup>
import { ref, computed, toRefs } from "vue";
import ShowMoreLess from "@/components/ui/ShowMoreLess.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import { useLiteratures } from "@/composables/useLiteratures";
import { useLiteratureByTheme } from "@/composables/useLiteratureByTheme";
import { useLiteratureByJurisdiction } from "@/composables/useLiteratureByJurisdiction";

const props = defineProps({
  label: { type: String, default: "Related Literature" },
  tooltip: { type: String, default: "" },
  themes: { type: String, default: "" },
  jurisdiction: { type: String, default: "" },
  literatureId: { type: String, default: "" },
  mode: {
    type: String,
    default: "themes",
    validator: (value) =>
      ["themes", "id", "both", "jurisdiction"].includes(value),
  },
  emptyValueBehavior: {
    type: Object,
    default: () => ({
      action: "display",
      fallback: "No related literature available",
    }),
  },
});

const showAll = ref(false);
const { themes, literatureId, jurisdiction, mode } = toRefs(props);

// Mode 'id'
const { data: literatureFromIds, isLoading: loadingIds } = useLiteratures(
  computed(() =>
    mode.value === "id" || mode.value === "both" ? literatureId.value : "",
  ),
);

const literatureTitles = computed(() => {
  if (!literatureFromIds.value) return [];
  return literatureFromIds.value
    .map((item) => ({
      id: item?.id,
      title: item?.Title,
    }))
    .filter((item) => item.title);
});

// Mode 'themes'
const { data: literatureFromThemes, isLoading: loadingThemes } =
  useLiteratureByTheme(
    computed(() =>
      mode.value === "themes" || mode.value === "both"
        ? themes.value
        : undefined,
    ),
  );

// Mode 'jurisdiction'
const { data: literatureFromJurisdiction, isLoading: loadingJurisdiction } =
  useLiteratureByJurisdiction(
    computed(() =>
      mode.value === "jurisdiction" || mode.value === "both"
        ? jurisdiction.value
        : "",
    ),
  );

// Merged for 'both' mode
const mergedLiterature = computed(() => {
  const idSet = new Set();
  const merged = [];

  literatureTitles.value.forEach((item) => {
    if (item.id && !idSet.has(item.id)) {
      merged.push(item);
      idSet.add(item.id);
    }
  });

  (literatureFromJurisdiction.value || []).forEach((item) => {
    if (item.id && !idSet.has(item.id)) {
      merged.push({
        id: item?.id,
        title: item?.Title,
      });
      idSet.add(item.id);
    }
  });

  (literatureFromThemes.value || []).forEach((item) => {
    if (item.id && !idSet.has(item.id)) {
      merged.push(item);
      idSet.add(item.id);
    }
  });

  return merged;
});

const fullLiteratureList = computed(() => {
  switch (mode.value) {
    case "id":
      return literatureTitles.value;
    case "themes":
      return literatureFromThemes.value || [];
    case "jurisdiction":
      return (literatureFromJurisdiction.value || [])
        .map((item) => ({
          id: item?.id,
          title: item?.Title,
        }))
        .filter((item) => item.title);
    case "both":
      return mergedLiterature.value;
    default:
      return [];
  }
});

const isLoading = computed(() => {
  switch (mode.value) {
    case "id":
      return loadingIds.value;
    case "themes":
      return loadingThemes.value;
    case "jurisdiction":
      return loadingJurisdiction.value;
    case "both":
      return (
        loadingIds.value || loadingThemes.value || loadingJurisdiction.value
      );
    default:
      return false;
  }
});

const hasRelatedLiterature = computed(
  () => fullLiteratureList.value.length > 0,
);

const shouldShowSection = computed(
  () =>
    isLoading.value ||
    hasRelatedLiterature.value ||
    (!hasRelatedLiterature.value &&
      props.emptyValueBehavior.action === "display"),
);

const displayedLiterature = computed(() => {
  const arr = fullLiteratureList.value;
  return !showAll.value && arr.length >= 5 ? arr.slice(0, 5) : arr;
});
</script>
