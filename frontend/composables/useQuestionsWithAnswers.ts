import { computed, type Ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { FullTableRequest, AnswerItem } from "@/types/api";
import { useFullTable } from "@/composables/useFullTable";

const processAnswerText = (answerText: string) => {
  if (typeof answerText === "string" && answerText.includes(",")) {
    return answerText
      .split(",")
      .map((s) => s.trim())
      .join("; ");
  }
  return answerText;
};

export { processAnswerText };

const fetchAnswersData = async (jurisdictions: string[]) => {
  const { apiClient } = useApiClient();

  // Fetch answers for all jurisdictions
  const allAnswers: Record<string, Record<string, string>> = {};

  for (const jurisdiction of jurisdictions) {
    const body: FullTableRequest = {
      table: "Answers",
      filters: [
        {
          column: "Jurisdictions Alpha-3 code",
          value: jurisdiction?.toUpperCase(),
        },
      ],
    };

    const data = await apiClient("/search/full_table", { body });

    const map: Record<string, string> = {};
    if (Array.isArray(data)) {
      for (const row of data as AnswerItem[]) {
        const rawQuestionId =
          row["Question ID"] || row["QuestionID"] || row["CoLD ID"] || row.ID;
        const rawColdId = row["CoLD ID"] || row["Answer ID"] || rawQuestionId;
        const answerValue = (row.Answer || row["Answer"] || "") as string;

        // Store by base question ID (without ISO3 prefix)
        const baseQuestionId = rawColdId
          ? String(rawColdId).replace(/^[A-Z]{3}_/, "")
          : String(rawQuestionId).replace(/^[A-Z]{3}_/, "");

        if (baseQuestionId) {
          map[baseQuestionId] = answerValue;
        }
      }
    }
    allAnswers[jurisdiction.toUpperCase()] = map;
  }

  return allAnswers;
};

export function useQuestionsWithAnswers(jurisdictions: Ref<string[]>) {
  const {
    data: questionsData,
    isLoading: questionsLoading,
    error: questionsError,
  } = useFullTable("Questions");

  const {
    data: answersData,
    isLoading: answersLoading,
    error: answersError,
  } = useQuery({
    queryKey: computed(() => ["answers", jurisdictions.value.join(",")]),
    queryFn: () => fetchAnswersData(jurisdictions.value),
    enabled: computed(() => jurisdictions.value.length > 0),
  });

  // Return a Map of answers per jurisdiction where the key is the question id (without iso3 code)
  const answersMap = computed(() => {
    return answersData.value || {};
  });

  return {
    questionsData,
    answersMap,
    loading: computed(() => questionsLoading.value),
    answersLoading: computed(() => answersLoading.value),
    error: computed(() => questionsError.value || answersError.value),
  };
}
