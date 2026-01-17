<template>
  <RelatedItemsList
    :items="fullItemsList"
    :is-loading="isLoading"
    base-path="/question"
    :empty-value-behavior="emptyValueBehavior"
  />
</template>

<script setup lang="ts">
import { computed, toRef } from "vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import { useRelatedQuestions } from "@/composables/useRelatedQuestions";
import type { RelatedItem, EmptyValueBehavior } from "@/types/ui";

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

const { questionList, questionLabels, isLoading } = useRelatedQuestions(
  toRef(props, "jurisdictionCode"),
  toRef(props, "questions"),
);

const fullItemsList = computed<RelatedItem[]>(() => {
  return questionList.value.map((q, idx) => ({
    id: `${props.jurisdictionCode}_${q}`,
    title: questionLabels.value[idx] || `${props.jurisdictionCode}_${q}`,
  }));
});
</script>
