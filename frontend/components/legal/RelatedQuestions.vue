<template>
  <RelatedItemsList
    :items="fullItemsList"
    :is-loading="isLoading"
    base-path="/question"
    :empty-value-behavior="emptyValueBehavior"
  />
</template>

<script setup>
import { computed, toRefs } from "vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import { useRelatedQuestions } from "@/composables/useRelatedQuestions";

const props = defineProps({
  jurisdictionCode: { type: String, default: "" },
  questions: { type: String, default: "" },
  emptyValueBehavior: { type: Object, default: () => ({ action: "hide" }) },
});

const { jurisdictionCode, questions, emptyValueBehavior } = toRefs(props);

const { questionList, questionLabels, isLoading } = useRelatedQuestions(
  jurisdictionCode,
  questions,
);

const fullItemsList = computed(() => {
  return questionList.value.map((q, idx) => ({
    id: `${jurisdictionCode.value}_${q}`,
    title: questionLabels.value[idx] || `${jurisdictionCode.value}_${q}`,
  }));
});
</script>
