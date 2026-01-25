import { computed, type Ref } from "vue";
import { useFullTableWithFilters } from "@/composables/useFullTable";
import type { AnswerResponse } from "@/types/entities/answer";

export interface Jurisdiction {
  name: string;
  code: string;
  region: string;
}

export interface AnswerGroup {
  answer: string;
  jurisdictions: Jurisdiction[];
}

export interface QuestionJurisdictionsData {
  questionTitle: string;
  answers: string[];
  answerGroups: Map<string, Jurisdiction[]>;
}

const EXCLUDED_ANSWERS = new Set([
  "No data",
  "Nothing found",
  "No information",
]);
const PRIORITY_ORDER = ["Yes", "No", "Not applicable"];

function processAnswers(
  records: AnswerResponse[],
  suffix: string,
): QuestionJurisdictionsData {
  // Filter to relevant records
  const relevantRecords = records.filter(
    (item) =>
      typeof item.ID === "string" &&
      item.ID.endsWith(suffix) &&
      item["Jurisdictions Irrelevant"] !== "Yes",
  );

  if (relevantRecords.length === 0) {
    return { questionTitle: "", answers: [], answerGroups: new Map() };
  }

  const questionTitle = relevantRecords[0]?.Question || "Missing Question";
  const answerGroups = new Map<string, Jurisdiction[]>();
  const uniqueAnswers = new Set<string>();

  for (const record of relevantRecords) {
    const answer = record.Answer;
    if (!answer || !answer.trim() || EXCLUDED_ANSWERS.has(answer)) {
      continue;
    }

    uniqueAnswers.add(answer);

    if (!answerGroups.has(answer)) {
      answerGroups.set(answer, []);
    }

    answerGroups.get(answer)!.push({
      name: record.Jurisdictions || "",
      code: record["Jurisdictions Alpha-3 Code"] || "",
      region: record["Jurisdictions Region"] || "",
    });
  }

  // Sort jurisdictions within each answer group
  for (const jurisdictions of answerGroups.values()) {
    jurisdictions.sort((a, b) => a.name.localeCompare(b.name));
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

export function useQuestionJurisdictions(suffix: Ref<string>) {
  const filters = computed(() => [
    { column: "ID" as const, value: suffix.value },
  ]);

  return useFullTableWithFilters<
    "Answers",
    AnswerResponse,
    QuestionJurisdictionsData
  >("Answers", filters, {
    select: (data) => processAnswers(data, suffix.value),
    enabled: computed(() => !!suffix.value),
  });
}
