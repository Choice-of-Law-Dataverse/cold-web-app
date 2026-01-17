<template>
  <RelatedItemsList
    :items="fullItemsList"
    :is-loading="isLoading"
    base-path="/court-decision"
    :empty-value-behavior="emptyValueBehavior"
  />
</template>

<script setup lang="ts">
import { computed, toRef } from "vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import { useCourtDecisionsByJurisdiction } from "@/composables/useCourtDecisionsByJurisdiction";
import type { RelatedItem, EmptyValueBehavior } from "@/types/ui";

const props = withDefaults(
  defineProps<{
    jurisdiction?: string;
    emptyValueBehavior?: EmptyValueBehavior;
  }>(),
  {
    jurisdiction: "",
    emptyValueBehavior: () => ({
      action: "display",
      fallback: "No court decisions available",
    }),
  },
);

const { data: courtDecisions, isLoading } = useCourtDecisionsByJurisdiction(
  toRef(props, "jurisdiction"),
);

const fullItemsList = computed<RelatedItem[]>(() => {
  if (!courtDecisions.value) return [];
  return courtDecisions.value
    .map((item) => ({
      id: item?.id ?? "",
      title: item?.["Case Title"] || item?.["Case Citation"] || "Untitled",
    }))
    .filter(
      (item): item is RelatedItem =>
        Boolean(item.id) &&
        Boolean(item.title) &&
        item.title !== "Untitled" &&
        item.title !== "NA",
    );
});
</script>
