import type { components } from "@/types/api-schema";
import { formatDate } from "@/utils/format";

export type RegionalInstrumentResponse =
  components["schemas"]["RegionalInstrumentRecord"];
export type RegionalInstrumentDetailResponse =
  components["schemas"]["RegionalInstrumentDetail"];

export type RegionalInstrument = RegionalInstrumentDetailResponse & {
  displayTitle: string;
  literature?: string;
  regionalLegalProvisions?: string;
};

export function processRegionalInstrument(
  raw: RegionalInstrumentDetailResponse,
): RegionalInstrument {
  const literature = raw.relations.literature
    .map((l) => l.coldId)
    .filter(Boolean)
    .join(",");

  const regionalLegalProvisions = raw.relations.regionalLegalProvisions
    .map((p) => p.coldId)
    .filter(Boolean)
    .join(",");

  return {
    ...raw,
    date: formatDate(raw.date),
    displayTitle: raw.title || "",
    literature: literature || undefined,
    regionalLegalProvisions: regionalLegalProvisions || undefined,
  };
}
