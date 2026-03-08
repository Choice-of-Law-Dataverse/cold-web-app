import type { components } from "@/types/api-schema";
import { formatDate } from "@/utils/format";

export type RegionalInstrumentResponse =
  components["schemas"]["RegionalInstrumentRecord"];

export type RegionalInstrument = RegionalInstrumentResponse & {
  displayTitle: string;
};

export function processRegionalInstrument(
  raw: RegionalInstrumentResponse,
): RegionalInstrument {
  return {
    ...raw,
    lastModified: formatDate(raw.lastModified || raw.created),
    date: formatDate(raw.date),
    displayTitle: raw.title || "",
  };
}
