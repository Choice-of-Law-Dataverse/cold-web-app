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

  const dataWithSuffix = Array.isArray(data)
    ? data.filter(
        (item) => typeof item.ID === "string" && item.ID.endsWith(suffix),
      )
    : [];

  const exactAnswerMatches = dataWithSuffix.filter(
    (item) => typeof item.Answer === "string" && item.Answer === answer,
  );

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

  let filtered = exactAnswerMatches.filter(
    (item) => item["Jurisdictions Irrelevant"] !== "Yes",
  );

  if (region && region !== "All") {
    filtered = filtered.filter(
      (item) => item["Jurisdictions Region"] === region,
    );
  }

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
