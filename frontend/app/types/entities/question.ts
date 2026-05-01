import type { components } from "@/types/api-schema";
import type { AnswerDetailResponse } from "@/types/entities/answer";

export type QuestionResponse = components["schemas"]["QuestionRecord"];
export type QuestionDetailResponse = components["schemas"]["QuestionDetail"];

export type Question = AnswerDetailResponse & {
  question?: string;
  jurisdictionCode: string;
};

type QuestionOrAnswerResponse = AnswerDetailResponse | QuestionDetailResponse;

export function processQuestion(raw: QuestionOrAnswerResponse): Question {
  const question =
    ("question" in raw && raw.question) ||
    raw.relations.questions[0]?.question ||
    undefined;

  return {
    ...raw,
    question,
    jurisdictionCode: raw.relations.jurisdictions[0]?.coldId || "",
  };
}
