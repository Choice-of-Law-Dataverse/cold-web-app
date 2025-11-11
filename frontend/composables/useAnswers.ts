import { computed, type Ref } from "vue";
import { useQueries } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { FullTableRequest, AnswerItem } from "@/types/api";

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

const fetchAnswersForJurisdiction = async (jurisdiction: string) => {
  const { apiClient } = useApiClient();

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

  if (!Array.isArray(data)) {
    return new Map<string, string>();
  }

  const entries = (data as AnswerItem[])
    .map((row) => {
      const rawQuestionId =
        row["Question ID"] || row["QuestionID"] || row["CoLD ID"] || row.ID;
      const rawColdId = row["CoLD ID"] || row["Answer ID"] || rawQuestionId;
      const answerValue = (row.Answer || row["Answer"] || "") as string;

      // Store by base question ID (without ISO3 prefix)
      const baseQuestionId = rawColdId
        ? String(rawColdId).replace(/^[A-Z]{3}_/, "")
        : String(rawQuestionId).replace(/^[A-Z]{3}_/, "");

      return [baseQuestionId, answerValue] as [string, string];
    })
    .filter(([key]) => Boolean(key));

  return new Map(entries);
};

export function useAnswersByJurisdictions(jurisdictions: Ref<string[]>) {
  const answersQueries = useQueries({
    queries: computed(() =>
      jurisdictions.value.map((jurisdiction) => ({
        queryKey: ["answers", jurisdiction.toUpperCase()],
        queryFn: () => fetchAnswersForJurisdiction(jurisdiction),
      })),
    ),
  });

  const data = computed(() => {
    const allAnswers = new Map<string, Map<string, string>>();

    jurisdictions.value.forEach((jurisdiction, index) => {
      const query = answersQueries.value[index];
      if (query?.data) {
        allAnswers.set(jurisdiction.toUpperCase(), query.data);
      }
    });

    return allAnswers;
  });

  const isLoading = computed(() => {
    return answersQueries.value.some((query) => query.isLoading);
  });

  const error = computed(() => {
    return answersQueries.value.find((query) => query.error)?.error;
  });

  return {
    data,
    isLoading,
    error,
  };
}
