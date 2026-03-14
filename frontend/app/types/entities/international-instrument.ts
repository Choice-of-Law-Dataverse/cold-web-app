import type { components } from "@/types/api-schema";

export type InternationalInstrumentResponse =
  components["schemas"]["InternationalInstrumentRecord"];
export type InternationalInstrumentDetailResponse =
  components["schemas"]["InternationalInstrumentDetail"];

export type InternationalInstrument = InternationalInstrumentDetailResponse & {
  displayTitle: string;
  displayUrl: string;
};

export function processInternationalInstrument(
  raw: InternationalInstrumentDetailResponse,
): InternationalInstrument {
  return {
    ...raw,
    displayTitle: raw.name || "",
    displayUrl: raw.url || "",
  };
}
