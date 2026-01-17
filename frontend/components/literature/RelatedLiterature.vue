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
import { useLiteratures } from "@/composables/useLiteratures";
import { useLiteratureByTheme } from "@/composables/useLiteratureByTheme";
import { useLiteratureByJurisdiction } from "@/composables/useLiteratureByJurisdiction";
import type { RelatedItem, EmptyValueBehavior } from "@/types/ui";

type LiteratureMode = "themes" | "id" | "both" | "jurisdiction";
type OupFilter = "onlyOup" | "noOup";

interface LiteratureItem {
  id: string;
  title: string;
  oupChapter?: boolean;
}

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
      action: "hide",
      fallback: "No related literature available",
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

const literatureTitles = computed<LiteratureItem[]>(() => {
  if (!literatureFromIds.value) return [];
  return literatureFromIds.value
    .filter((item): item is NonNullable<typeof item> => Boolean(item?.Title))
    .map((item) => ({
      id: item.id,
      title: item.Title!,
      oupChapter: Boolean(item["OUP JD Chapter"]),
    }));
});

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

const mergedLiterature = computed<LiteratureItem[]>(() => {
  const idSet = new Set<string>();
  const merged: LiteratureItem[] = [];

  literatureTitles.value.forEach((item) => {
    if (item.id && !idSet.has(item.id)) {
      merged.push(item);
      idSet.add(item.id);
    }
  });

  (literatureFromJurisdiction.value || []).forEach((item) => {
    if (item?.id && !idSet.has(item.id) && item.Title) {
      merged.push({
        id: item.id,
        title: item.Title,
        oupChapter: Boolean(item["OUP JD Chapter"]),
      });
      idSet.add(item.id);
    }
  });

  (literatureFromThemes.value || []).forEach((item) => {
    if (item?.id && !idSet.has(item.id) && item.title) {
      merged.push({
        id: item.id,
        title: item.title,
        oupChapter: Boolean(item["OUP JD Chapter"]),
      });
      idSet.add(item.id);
    }
  });

  return merged;
});

const fullLiteratureList = computed<RelatedItem[]>(() => {
  let items: LiteratureItem[] = [];

  switch (mode.value) {
    case "id":
      items = literatureTitles.value;
      break;
    case "themes":
      items = (literatureFromThemes.value || [])
        .filter((item) => item?.title)
        .map((item) => ({
          id: item.id,
          title: item.title!,
          oupChapter: Boolean(item["OUP JD Chapter"]),
        }));
      break;
    case "jurisdiction":
      items = (literatureFromJurisdiction.value || [])
        .filter((item) => item?.Title)
        .map((item) => ({
          id: item!.id,
          title: item!.Title!,
          oupChapter: Boolean(item!["OUP JD Chapter"]),
        }));
      break;
    case "both":
      items = mergedLiterature.value;
      break;
    default:
      items = [];
  }

  return items
    .filter((item) =>
      oupFilter.value === "onlyOup"
        ? item.oupChapter === true
        : !item.oupChapter,
    )
    .map(({ id, title }) => ({ id, title }));
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
