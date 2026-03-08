import type { components } from "@/types/api-schema";
import { formatDate } from "@/utils/format";

export type QuestionResponse = components["schemas"]["AnswerRecord"];

export type Question = QuestionResponse & {
  courtDecisionsIdList: string[];
  jurisdictionCode: string;
};

export function processQuestion(raw: QuestionResponse): Question {
  const courtDecisionsId = raw.courtDecisionsId;

  return {
    ...raw,
    lastModified: formatDate(raw.lastModified || raw.created),
    courtDecisionsIdList:
      typeof courtDecisionsId === "string"
        ? courtDecisionsId.split(",").map((caseId) => caseId.trim())
        : [],
    jurisdictionCode: raw.jurisdictionsAlpha3Code || "",
  };
}
