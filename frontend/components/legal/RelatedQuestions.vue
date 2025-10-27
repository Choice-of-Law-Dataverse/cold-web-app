<template>
  <div v-if="shouldDisplay">
    <h4 v-if="label" class="label ">
      <span class="flex flex-row items-center">
      {{ label }}
      <InfoPopover v-if="tooltip" :text="tooltip" />
      </span>
    </h4>
    <ul v-if="questionList.length">
      <li v-for="(q, idx) in questionList" :key="idx">
        <NuxtLink :to="`/question/${jurisdictionCode}_${q}`">
          {{ questionLabels[idx] || jurisdictionCode + "_" + q }}
        </NuxtLink>
      </li>
    </ul>
    <span v-else-if="isLoading">Loading related questions...</span>
    <span v-else>No related questions.</span>
  </div>
</template>

<script setup>
import { computed, toRefs } from "vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import { useRelatedQuestions } from "@/composables/useRelatedQuestions";

const props = defineProps({
  label: { type: String, default: "Related Questions" },
  jurisdictionCode: { type: String, default: "" },
  questions: { type: String, default: "" },
  emptyValueBehavior: { type: Object, default: () => ({ action: "hide" }) },
  tooltip: { type: String, default: "" },
});

const { jurisdictionCode, questions, emptyValueBehavior } = toRefs(props);

const { questionList, questionLabels, isLoading } = useRelatedQuestions(
  jurisdictionCode,
  questions,
);

const shouldDisplay = computed(() => {
  if (
    emptyValueBehavior.value?.action === "hide" &&
    questionList.value.length === 0
  ) {
    return false;
  }
  return true;
});
</script>
