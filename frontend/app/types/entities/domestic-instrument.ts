import type { components } from "@/types/api-schema";
import { formatDate } from "@/utils/format";

export type DomesticInstrumentResponse =
  components["schemas"]["DomesticInstrumentRecord"];
export type DomesticInstrumentDetailResponse =
  components["schemas"]["DomesticInstrumentDetail"];

export type DomesticInstrument = DomesticInstrumentDetailResponse & {
  displayTitle: string;
  compatibility?: boolean;
  rankingDisplayOrder?: string;
};

export function isTruthy(val: string | boolean | null | undefined): boolean {
  if (typeof val === "boolean") return val;
  return val === "true" || val === "1" || val === "Yes";
}

export function processDomesticInstrument(
  raw: DomesticInstrumentDetailResponse,
): DomesticInstrument {
  const hcchCompat = isTruthy(raw.compatibleWithTheHcchPrinciples);
  const uncitralCompat = isTruthy(raw.compatibleWithTheUncitralModelLaw);
  const hasCompatibility = hcchCompat || uncitralCompat;

  const titleInEnglish = raw.titleInEnglish || raw.officialTitle || "";
  const displayTitle =
    raw.abbreviation || titleInEnglish || raw.officialTitle || String(raw.id);

  const provisions = raw.relations.domesticLegalProvisions;
  const rankingOrders = provisions
    .filter((p) => p.rankingDisplayOrder)
    .map((p) => `${p.coldId}:${p.rankingDisplayOrder}`)
    .join(",");

  return {
    ...raw,
    date: formatDate(raw.date),
    publicationDate: formatDate(raw.publicationDate),
    displayTitle,
    compatibility: hasCompatibility ? true : undefined,
    rankingDisplayOrder: rankingOrders || undefined,
  };
}
