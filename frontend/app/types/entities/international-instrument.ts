import type { components } from "@/types/api-schema";
import { formatDate } from "@/utils/format";

export type InternationalInstrumentResponse =
  components["schemas"]["InternationalInstrumentRecord"];

export type InternationalInstrument = InternationalInstrumentResponse & {
  displayTitle: string;
  displayUrl: string;
};

export function processInternationalInstrument(
  raw: InternationalInstrumentResponse,
): InternationalInstrument {
  return {
    ...raw,
    publicationDate: formatDate(raw.publicationDate || raw.date),
    displayTitle: raw.titleInEnglish || raw.name || "",
    displayUrl: raw.url || "",
  };
}
