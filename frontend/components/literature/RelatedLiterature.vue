<template>
  <RelatedItemsList
    :items="fullLiteratureList"
    :is-loading="isLoading"
    base-path="/literature"
    :empty-value-behavior="emptyValueBehavior"
  />
</template>

<script setup lang="ts">
import { computed, toRef } from "vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import { useLiteratures } from "@/composables/useRecordDetails";
import { useLiteratureByTheme } from "@/composables/useLiteratureByTheme";
import { useLiteratureByJurisdiction } from "@/composables/useFullTable";
import type { Literature } from "@/types/entities/literature";
import type { RelatedItem, EmptyValueBehavior } from "@/types/ui";

type LiteratureMode = "themes" | "id" | "both" | "jurisdiction";
type OupFilter = "onlyOup" | "noOup";

const props = withDefaults(
  defineProps<{
    themes?: string;
    jurisdiction?: string;
    literatureId?: string;
    mode?: LiteratureMode;
    oupFilter: OupFilter;
    emptyValueBehavior?: EmptyValueBehavior;
  }>(),
  {
    themes: "",
    jurisdiction: "",
    literatureId: "",
    mode: "themes",
    emptyValueBehavior: () => ({
      action: "display",
    }),
  },
);

const mode = toRef(props, "mode");
const oupFilter = toRef(props, "oupFilter");

const { data: literatureFromIds, isLoading: loadingIds } = useLiteratures(
  computed(() =>
    mode.value === "id" || mode.value === "both" ? props.literatureId : "",
  ),
);

const { data: literatureFromThemes, isLoading: loadingThemes } =
  useLiteratureByTheme(
    computed(() =>
      mode.value === "themes" || mode.value === "both"
        ? props.themes
        : undefined,
    ),
  );

const { data: literatureFromJurisdiction, isLoading: loadingJurisdiction } =
  useLiteratureByJurisdiction(
    computed(() =>
      mode.value === "jurisdiction" || mode.value === "both"
        ? props.jurisdiction
        : "",
    ),
  );

const mergedLiterature = computed<Literature[]>(() => {
  const idSet = new Set<string>();
  const merged: Literature[] = [];

  const addIfNew = (item: Literature | undefined) => {
    if (item?.id && item.displayTitle && !idSet.has(item.id)) {
      merged.push(item);
      idSet.add(item.id);
    }
  };

  (literatureFromIds.value || []).forEach(addIfNew);
  (literatureFromJurisdiction.value || []).forEach(addIfNew);
  (literatureFromThemes.value || []).forEach(addIfNew);

  return merged;
});

const fullLiteratureList = computed<RelatedItem[]>(() => {
  let items: Literature[] = [];

  switch (mode.value) {
    case "id":
      items = (literatureFromIds.value || []).filter(
        (item): item is Literature => Boolean(item?.displayTitle),
      );
      break;
    case "themes":
      items = (literatureFromThemes.value || []).filter(
        (item) => item.displayTitle !== "Untitled",
      );
      break;
    case "jurisdiction":
      items = (literatureFromJurisdiction.value || []).filter(
        (item) => item.displayTitle !== "Untitled",
      );
      break;
    case "both":
      items = mergedLiterature.value.filter(
        (item) => item.displayTitle !== "Untitled",
      );
      break;
    default:
      items = [];
  }

  return items
    .filter((item) =>
      oupFilter.value === "onlyOup" ? item.isOupChapter : !item.isOupChapter,
    )
    .map(({ id, displayTitle }) => ({ id, title: displayTitle }));
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
