<template>
  <RelatedItemsList
    :items="items"
    :is-loading="isLoading"
    base-path="/question"
    :empty-value-behavior="emptyValueBehavior"
  />
</template>

<script setup lang="ts">
import { toRef } from "vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import { useRelatedQuestions } from "@/composables/useRecordDetails";
import type { EmptyValueBehavior } from "@/types/ui";

const props = withDefaults(
  defineProps<{
    jurisdictionCode?: string;
    questions?: string;
    emptyValueBehavior?: EmptyValueBehavior;
  }>(),
  {
    jurisdictionCode: "",
    questions: "",
    emptyValueBehavior: () => ({ action: "hide" }),
  },
);

const { items, isLoading } = useRelatedQuestions(
  toRef(props, "jurisdictionCode"),
  toRef(props, "questions"),
);
</script>
