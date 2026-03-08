import type { components } from "@/types/api-schema";

export type LiteratureResponse = components["schemas"]["LiteratureRecord"];
export type LiteratureDetailResponse =
  components["schemas"]["LiteratureDetail"];

export interface LiteratureDisplay {
  id: string | number | null | undefined;
  displayTitle: string;
  isOupChapter: boolean;
}

export type Literature = LiteratureDetailResponse & LiteratureDisplay;

export function processLiterature(raw: LiteratureDetailResponse): Literature {
  return {
    ...raw,
    displayTitle: raw.title || "Untitled",
    isOupChapter: Boolean(raw.oupJdChapter),
  };
}

export function processLiteratureRecord(
  raw: LiteratureResponse,
): LiteratureDisplay {
  return {
    id: raw.id,
    displayTitle: raw.title || "Untitled",
    isOupChapter: Boolean(raw.oupJdChapter),
  };
}
