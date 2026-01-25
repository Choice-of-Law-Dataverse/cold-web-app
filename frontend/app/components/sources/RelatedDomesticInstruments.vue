<template>
  <RelatedItemsList
    :items="data"
    :is-loading="isLoading"
    base-path="/domestic-instrument"
    :empty-value-behavior="emptyValueBehavior"
  />
</template>

<script setup lang="ts">
import { toRef } from "vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import { useDomesticInstrumentsByJurisdiction } from "@/composables/useDomesticInstrumentsByJurisdiction";
import type { EmptyValueBehavior } from "@/types/ui";

const props = withDefaults(
  defineProps<{
    jurisdiction?: string;
    emptyValueBehavior?: EmptyValueBehavior;
  }>(),
  {
    jurisdiction: "",
    emptyValueBehavior: () => ({
      action: "display",
    }),
  },
);

const { data, isLoading } = useDomesticInstrumentsByJurisdiction(
  toRef(props, "jurisdiction"),
);
</script>
