import type { components } from "@/types/api-schema";
import { formatDate } from "@/utils/format";

export type DomesticInstrumentResponse =
  components["schemas"]["DomesticInstrumentRecord"];

export type DomesticInstrument = DomesticInstrumentResponse & {
  displayTitle: string;
  compatibility?: boolean;
};

export function processDomesticInstrument(
  raw: DomesticInstrumentResponse,
): DomesticInstrument {
  const hasCompatibility =
    raw.compatibleWithTheUncitralModelLaw === true ||
    raw.compatibleWithTheHcchPrinciples === true;

  const titleInEnglish = raw.titleInEnglish || raw.officialTitle || "";
  const displayTitle =
    raw.abbreviation ||
    titleInEnglish ||
    raw.officialTitle ||
    String(raw.id || "");

  return {
    ...raw,
    date: formatDate(raw.date),
    publicationDate: formatDate(raw.publicationDate),
    lastModified: formatDate(raw.lastModified || raw.created),
    displayTitle,
    compatibility: hasCompatibility ? true : undefined,
  };
}
