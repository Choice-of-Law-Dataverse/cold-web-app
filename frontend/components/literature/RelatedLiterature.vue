<template>
  <RelatedItemsList
    :items="fullLiteratureList"
    :is-loading="isLoading"
    base-path="/literature"
    :empty-value-behavior="emptyValueBehavior"
  />
</template>

<script setup>
import { computed, toRefs } from "vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
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
      action: "hide",
      fallback: "No related literature available",
    }),
  },
});

const { themes, literatureId, jurisdiction, mode } = toRefs(props);

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

const { data: literatureFromThemes, isLoading: loadingThemes } =
  useLiteratureByTheme(
    computed(() =>
      mode.value === "themes" || mode.value === "both"
        ? themes.value
        : undefined,
    ),
  );

const { data: literatureFromJurisdiction, isLoading: loadingJurisdiction } =
  useLiteratureByJurisdiction(
    computed(() =>
      mode.value === "jurisdiction" || mode.value === "both"
        ? jurisdiction.value
        : "",
    ),
  );

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
</script>
