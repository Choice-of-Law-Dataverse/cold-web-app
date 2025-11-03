<template>
  <RelatedItemsList
    :items="fullItemsList"
    :is-loading="isLoading"
    base-path="/domestic-instrument"
    :empty-value-behavior="emptyValueBehavior"
  />
</template>

<script setup>
import { computed, toRefs } from "vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import { useDomesticInstrumentsByJurisdiction } from "@/composables/useDomesticInstrumentsByJurisdiction";

const props = defineProps({
  jurisdiction: { type: String, default: "" },
  emptyValueBehavior: {
    type: Object,
    default: () => ({
      action: "display",
      fallback: "No domestic instruments available",
    }),
  },
});

const { jurisdiction } = toRefs(props);

const { data: domesticInstruments, isLoading } =
  useDomesticInstrumentsByJurisdiction(computed(() => jurisdiction.value));

const fullItemsList = computed(() => {
  if (!domesticInstruments.value) return [];
  return domesticInstruments.value
    .map((item) => ({
      id: item?.id,
      title:
        item?.["Title (in English)"] || item?.["Abbreviation"] || "Untitled",
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
