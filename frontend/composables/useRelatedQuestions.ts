import { computed } from "vue";
import { useRecordDetailsList } from "@/composables/useRecordDetails";

export function useRelatedQuestions(
  jurisdictionCode: Ref<string>,
  questions: Ref<string>,
) {
  const questionList = computed(() =>
    questions.value
      ? questions.value
          .split(",")
          .map((q) => q.trim())
          .filter((q) => q)
      : [],
  );

  const compositeIds = computed(() =>
    jurisdictionCode.value && questionList.value.length
      ? questionList.value.map((qid) => `${jurisdictionCode.value}_${qid}`)
      : [],
  );

  const results = useRecordDetailsList(
    computed(() => "Answers"),
    compositeIds,
  );

  const questionLabels = computed(() => {
    return questionList.value.map((qid) => {
      const id = `${jurisdictionCode.value}_${qid}`;
      const rec = (results.data.value as Record<string, Record<string, unknown>> | undefined)?.[id];
      return rec?.Question || id;
    });
  });

  return {
    questionList,
    questionLabels,
    ...results,
  };
}
