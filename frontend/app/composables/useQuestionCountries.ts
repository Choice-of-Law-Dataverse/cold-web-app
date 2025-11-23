import { computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { FullTableRequest } from "@/types/api";

const fetchQuestionCountries = async ({ suffix }: { suffix: string }) => {
  if (!suffix) {
    return { answers: [], questionTitle: "" };
  }

  const { apiClient } = useApiClient();

  const body: FullTableRequest = {
    table: "Answers",
    filters: [{ column: "ID", value: suffix }],
  };

  const data = await apiClient("/search/full_table", { body });

  const dataWithSuffix = Array.isArray(data)
    ? data.filter(
        (item) => typeof item.ID === "string" && item.ID.endsWith(suffix),
      )
    : [];

  let questionTitle = "";
  if (
    dataWithSuffix.length > 0 &&
    typeof dataWithSuffix[0].Question === "string"
  ) {
    questionTitle = dataWithSuffix[0].Question;
  }

  // Filter out irrelevant jurisdictions and structure data by answer
  const relevantData = dataWithSuffix.filter(
    (item) => item["Jurisdictions Irrelevant"] !== "Yes",
  );

  return {
    answers: relevantData,
    questionTitle: questionTitle || "Missing Question",
  };
};

export function useQuestionCountries(suffix: Ref<string>) {
  return useQuery({
    queryKey: ["questionCountries", suffix],
    queryFn: () =>
      fetchQuestionCountries({
        suffix: suffix.value,
      }),
    enabled: computed(() => !!suffix.value),
  });
}
