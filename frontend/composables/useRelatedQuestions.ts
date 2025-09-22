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
    // Create a mapping object from the array data using compositeIds as keys
    const dataMap = compositeIds.value.reduce((acc, id, index) => {
      const record = results.data.value?.[index];
      if (record) {
        acc[id] = record;
      }
      return acc;
    }, {} as Record<string, Record<string, unknown>>);

    return questionList.value.map((qid) => {
      const id = `${jurisdictionCode.value}_${qid}`;
      const rec = dataMap[id];
      return rec?.Question || id;
    });
  });

  return {
    questionList,
    questionLabels,
    ...results,
  };
}
