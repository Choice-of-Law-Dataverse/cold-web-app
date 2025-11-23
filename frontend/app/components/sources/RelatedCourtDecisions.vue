<template>
  <RelatedItemsList
    :items="fullItemsList"
    :is-loading="isLoading"
    base-path="/court-decision"
    entity-type="court-decision"
    :empty-value-behavior="emptyValueBehavior"
  />
</template>

<script setup>
import { computed, toRefs } from "vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import { useCourtDecisionsByJurisdiction } from "@/composables/useCourtDecisionsByJurisdiction";

const props = defineProps({
  jurisdiction: { type: String, default: "" },
  emptyValueBehavior: {
    type: Object,
    default: () => ({
      action: "display",
      fallback: "No court decisions available",
    }),
  },
});

const { jurisdiction } = toRefs(props);

const { data: courtDecisions, isLoading } = useCourtDecisionsByJurisdiction(
  computed(() => jurisdiction.value),
);

const fullItemsList = computed(() => {
  if (!courtDecisions.value) return [];
  return courtDecisions.value
    .map((item) => ({
      id: item?.id,
      title: item?.["Case Title"] || item?.["Case Citation"] || "Untitled",
    }))
    .filter(
      (item) =>
        item.id &&
        item.title &&
        item.title !== "Untitled" &&
        item.title !== "NA",
    );
});
</script>
