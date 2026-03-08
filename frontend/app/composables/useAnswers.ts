import { computed, type Ref } from "vue";
import { useQueries } from "@tanstack/vue-query";
import type createClient from "openapi-fetch";
import { useApiClient } from "@/composables/useApiClient";
import { fetchFullTableData } from "@/composables/useFullTable";
import type { paths } from "@/types/api-schema";

type ApiClient = ReturnType<typeof createClient<paths>>;

const processAnswerText = (answerText: string) => {
  if (typeof answerText === "string" && answerText.includes(",")) {
    return answerText
      .split(",")
      .map((s: string) => s.trim())
      .join("; ");
  }
  return answerText;
};

export { processAnswerText };

const fetchAnswersForJurisdiction = async (
  client: ApiClient,
  jurisdiction: string,
) => {
  const data = await fetchFullTableData(client, "Answers", [
    {
      column: "jurisdictionsAlpha3Code",
      value: jurisdiction?.toUpperCase(),
    },
  ]);

  const entries = data
    .map((row) => {
      const rawQuestionId = row.questionId || row.coldId || row.id;
      const rawColdId = row.coldId || row.answerId || rawQuestionId;
      const answerValue = row.answer || "";

      const baseQuestionId = rawColdId
        ? String(rawColdId).replace(/^[A-Z]{3}_/, "")
        : String(rawQuestionId).replace(/^[A-Z]{3}_/, "");

      return [baseQuestionId, answerValue] as [string, string];
    })
    .filter(([key]: [string, string]) => Boolean(key));

  return new Map(entries);
};

export function useAnswersByJurisdictions(jurisdictions: Ref<string[]>) {
  const { client } = useApiClient();

  const answersQueries = useQueries({
    queries: computed(() =>
      jurisdictions.value.map((jurisdiction) => ({
        queryKey: ["answers", jurisdiction.toUpperCase()],
        queryFn: () => fetchAnswersForJurisdiction(client, jurisdiction),
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
