import type { components } from "@/types/api-schema";

export type InternationalInstrumentResponse =
  components["schemas"]["InternationalInstrumentRecord"];
export type InternationalInstrumentDetailResponse =
  components["schemas"]["InternationalInstrumentDetail"];

export type InternationalInstrument = InternationalInstrumentDetailResponse & {
  displayTitle: string;
  displayUrl: string;
  literature?: string;
  specialists?: string;
  selectedProvisions?: string;
};

export function processInternationalInstrument(
  raw: InternationalInstrumentDetailResponse,
): InternationalInstrument {
  const literature = raw.relations.literature
    .map((l) => l.coldId)
    .filter(Boolean)
    .join(",");

  const specialists = raw.relations.specialists
    .map((s) => s.specialist)
    .filter(Boolean)
    .join(", ");

  const selectedProvisions = raw.relations.internationalLegalProvisions
    .map((p) => p.coldId)
    .filter(Boolean)
    .join(",");

  return {
    ...raw,
    displayTitle: raw.name || "",
    displayUrl: raw.url || "",
    literature: literature || undefined,
    specialists: specialists || undefined,
    selectedProvisions: selectedProvisions || undefined,
  };
}
