<template>
  <RelatedItemsList
    :items="fullItemsList"
    :is-loading="isLoading"
    base-path="/domestic-instrument"
    :empty-value-behavior="emptyValueBehavior"
  />
</template>

<script setup lang="ts">
import { computed, toRef } from "vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import { useDomesticInstrumentsByJurisdiction } from "@/composables/useDomesticInstrumentsByJurisdiction";
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
      fallback: "No domestic instruments available",
    }),
  },
);

const { data: domesticInstruments, isLoading } =
  useDomesticInstrumentsByJurisdiction(toRef(props, "jurisdiction"));

const fullItemsList = computed<RelatedItem[]>(() => {
  if (!domesticInstruments.value) return [];
  return domesticInstruments.value
    .map((item) => ({
      id: item?.id ?? "",
      title: item?.["Title (in English)"] || item?.Abbreviation || "Untitled",
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
