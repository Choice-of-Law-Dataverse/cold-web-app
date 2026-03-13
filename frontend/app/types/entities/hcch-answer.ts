import type { components } from "@/types/api-schema";

export type HcchAnswerDetailResponse =
  components["schemas"]["HcchAnswerDetail"];

export type HcchAnswer = HcchAnswerDetailResponse;

export function processHcchAnswer(raw: HcchAnswerDetailResponse): HcchAnswer {
  return raw;
}
