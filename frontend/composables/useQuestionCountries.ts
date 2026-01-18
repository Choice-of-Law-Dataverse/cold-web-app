import { computed, type Ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { FullTableRequest } from "@/types/api";

interface AnswerRecord {
  ID: string;
  Answer: string;
  Question: string;
  Jurisdictions: string;
  "Jurisdictions Alpha-3 Code"?: string;
  "Jurisdictions Alpha-3 code"?: string;
  "Jurisdictions Region": string;
  "Jurisdictions Irrelevant"?: string;
}

export interface Country {
  name: string;
  code: string;
  region: string;
}

export interface AnswerGroup {
  answer: string;
  countries: Country[];
}

export interface QuestionCountriesData {
  questionTitle: string;
  answers: string[];
  answerGroups: Map<string, Country[]>;
}

const EXCLUDED_ANSWERS = new Set([
  "No data",
  "Nothing found",
  "No information",
]);
const PRIORITY_ORDER = ["Yes", "No", "Not applicable"];

function processAnswers(records: AnswerRecord[]): QuestionCountriesData {
  if (records.length === 0) {
    return { questionTitle: "", answers: [], answerGroups: new Map() };
  }

  const questionTitle = records[0]?.Question || "Missing Question";
  const answerGroups = new Map<string, Country[]>();
  const uniqueAnswers = new Set<string>();

  for (const record of records) {
    const answer = record.Answer;
    if (
      typeof answer !== "string" ||
      !answer.trim() ||
      EXCLUDED_ANSWERS.has(answer)
    ) {
      continue;
    }

    uniqueAnswers.add(answer);

    if (!answerGroups.has(answer)) {
      answerGroups.set(answer, []);
    }

    answerGroups.get(answer)!.push({
      name: record.Jurisdictions,
      code:
        record["Jurisdictions Alpha-3 Code"] ||
        record["Jurisdictions Alpha-3 code"] ||
        "",
      region: record["Jurisdictions Region"],
    });
  }

  // Sort countries within each answer group
  for (const countries of answerGroups.values()) {
    countries.sort((a, b) => a.name.localeCompare(b.name));
  }

  // Sort answers with priority order first
  const sortedAnswers: string[] = [];
  for (const answer of PRIORITY_ORDER) {
    if (uniqueAnswers.has(answer)) {
      sortedAnswers.push(answer);
      uniqueAnswers.delete(answer);
    }
  }
  sortedAnswers.push(
    ...Array.from(uniqueAnswers).sort((a, b) => a.localeCompare(b)),
  );

  return { questionTitle, answers: sortedAnswers, answerGroups };
}

async function fetchQuestionCountries(
  suffix: string,
): Promise<QuestionCountriesData> {
  if (!suffix) {
    return { questionTitle: "", answers: [], answerGroups: new Map() };
  }

  const { apiClient } = useApiClient();
  const body: FullTableRequest = {
    table: "Answers",
    filters: [{ column: "ID", value: suffix }],
  };

  const data = await apiClient<AnswerRecord[]>("/search/full_table", { body });

  const relevantRecords = data.filter(
    (item) =>
      typeof item.ID === "string" &&
      item.ID.endsWith(suffix) &&
      item["Jurisdictions Irrelevant"] !== "Yes",
  );

  return processAnswers(relevantRecords);
}

export function useQuestionCountries(suffix: Ref<string>) {
  return useQuery({
    queryKey: ["questionCountries", suffix],
    queryFn: () => fetchQuestionCountries(suffix.value),
    enabled: computed(() => !!suffix.value),
  });
}
