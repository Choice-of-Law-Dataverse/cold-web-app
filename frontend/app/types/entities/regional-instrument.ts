import type { components } from "@/types/api-schema";

export type RegionalInstrumentResponse =
  components["schemas"]["RegionalInstrumentRecord"];
export type RegionalInstrumentDetailResponse =
  components["schemas"]["RegionalInstrumentDetail"];

export type RegionalInstrument = RegionalInstrumentDetailResponse & {
  displayTitle: string;
};

export function processRegionalInstrument(
  raw: RegionalInstrumentDetailResponse,
): RegionalInstrument {
  return {
    ...raw,
    displayTitle: raw.title || "",
  };
}
