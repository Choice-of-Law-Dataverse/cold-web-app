import type { components } from "@/types/api-schema";

export type JurisdictionResponse = components["schemas"]["JurisdictionRecord"];
export type JurisdictionDetailResponse =
  components["schemas"]["JurisdictionDetail"];

export type Jurisdiction = JurisdictionDetailResponse;

export function processJurisdiction(
  raw: JurisdictionDetailResponse,
): Jurisdiction {
  return raw;
}
