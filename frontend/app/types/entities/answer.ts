import type { components } from "@/types/api-schema";

export type AnswerResponse = components["schemas"]["AnswerRecord"];
export type AnswerDetailResponse = components["schemas"]["AnswerDetail"];

export type Answer = AnswerDetailResponse;

export function processAnswer(raw: AnswerDetailResponse): Answer {
  return raw;
}
