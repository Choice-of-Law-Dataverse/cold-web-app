import type { components } from "@/types/api-schema";
import type { AnswerDetailResponse } from "@/types/entities/answer";

export type QuestionResponse = components["schemas"]["AnswerRecord"];
export type QuestionDetailResponse = components["schemas"]["QuestionDetail"];

export type Question = AnswerDetailResponse & {
  question?: string;
  themes?: string;
  jurisdictions?: string;
  courtDecisionsIdList: string[];
  jurisdictionCode: string;
  courtDecisionsId?: string;
  domesticInstrumentsId?: string;
  domesticLegalProvisions?: string;
  relatedLiterature?: string;
};

type QuestionOrAnswerResponse = AnswerDetailResponse | QuestionDetailResponse;

export function processQuestion(raw: QuestionOrAnswerResponse): Question {
  const courtDecisionsColdIds = raw.relations.courtDecisions
    .map((cd) => cd.coldId)
    .filter(Boolean) as string[];

  const domesticLegalProvisions = raw.relations.domesticLegalProvisions
    .map((p) => p.coldId)
    .filter(Boolean)
    .join(",");

  const question =
    ("question" in raw && raw.question) ||
    raw.relations.questions[0]?.question ||
    undefined;

  const themes =
    raw.relations.themes
      .map((t) => t.theme)
      .filter(Boolean)
      .join(", ") || undefined;

  const jurisdictions =
    raw.relations.jurisdictions
      .map((j) => j.name)
      .filter(Boolean)
      .join(", ") || undefined;

  return {
    ...raw,
    question,
    themes,
    jurisdictions,
    courtDecisionsIdList: courtDecisionsColdIds,
    courtDecisionsId: courtDecisionsColdIds.join(",") || undefined,
    domesticInstrumentsId:
      raw.relations.domesticInstruments
        .map((di) => di.coldId)
        .filter(Boolean)
        .join(",") || undefined,
    jurisdictionCode: raw.relations.jurisdictions[0]?.coldId || "",
    domesticLegalProvisions: domesticLegalProvisions || undefined,
    relatedLiterature: raw.relations.literature.length > 0 ? "has" : undefined,
  };
}
