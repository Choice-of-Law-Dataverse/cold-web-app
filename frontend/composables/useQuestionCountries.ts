import { computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { FullTableRequest } from "@/types/api";

const fetchQuestionCountries = async ({
  suffix,
  answer,
  region,
}: {
  suffix: string;
  answer: string;
  region: string;
}) => {
  if (!suffix || !answer) {
    return { countries: [], questionTitle: "" };
  }

  const { apiClient } = useApiClient();

  const body: FullTableRequest = {
    table: "Answers",
    filters: [
      { column: "ID", value: suffix },
      { column: "Answer", value: answer },
    ],
  };

  const data = await apiClient("/search/full_table", { body });

  // Ensure we only keep rows whose ID actually ends with the requested suffix
  const dataWithSuffix = Array.isArray(data)
    ? data.filter(
        (item) => typeof item.ID === "string" && item.ID.endsWith(suffix),
      )
    : [];

  // Enforce exact match on the Answer field (API may do substring matching)
  const exactAnswerMatches = dataWithSuffix.filter(
    (item) => typeof item.Answer === "string" && item.Answer === answer,
  );

  // Extract question title from an exact-answer match if available, otherwise fall back
  let questionTitle = "";
  if (
    exactAnswerMatches.length > 0 &&
    typeof exactAnswerMatches[0].Question === "string"
  ) {
    questionTitle = exactAnswerMatches[0].Question;
  } else if (
    dataWithSuffix.length > 0 &&
    typeof dataWithSuffix[0].Question === "string"
  ) {
    questionTitle = dataWithSuffix[0].Question;
  }

  // Start from exact-answer matches so "No" does not match "No Data"
  let filtered = exactAnswerMatches.filter(
    (item) => item["Jurisdictions Irrelevant"] !== "Yes",
  );

  // Apply region filter if not 'All'
  if (region && region !== "All") {
    filtered = filtered.filter(
      (item) => item["Jurisdictions Region"] === region,
    );
  }

  // Map to objects with name and code, then sort by name
  const countries = filtered
    .map((item) => ({
      name: item.Jurisdictions,
      code: item["Jurisdictions Alpha-3 code"],
    }))
    .sort((a, b) => a.name.localeCompare(b.name));

  return {
    countries,
    questionTitle: questionTitle || "Missing Question",
  };
};

export function useQuestionCountries(
  suffix: Ref<string>,
  answer: Ref<string>,
  region: Ref<string>,
) {
  return useQuery({
    queryKey: ["questionCountries", suffix, answer, region],
    queryFn: () =>
      fetchQuestionCountries({
        suffix: suffix.value,
        answer: answer.value,
        region: region.value,
      }),
    enabled: computed(() => !!suffix.value && !!answer.value),
  });
}
