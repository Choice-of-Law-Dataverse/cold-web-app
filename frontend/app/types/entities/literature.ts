import type { components } from "@/types/api-schema";
import { formatDate } from "@/utils/format";

export type LiteratureResponse = components["schemas"]["LiteratureRecord"];

export type Literature = LiteratureResponse & {
  displayTitle: string;
  isOupChapter: boolean;
};

export function processLiterature(raw: LiteratureResponse): Literature {
  return {
    ...raw,
    displayTitle: raw.title || "Untitled",
    isOupChapter: Boolean(raw.oupJdChapter),
    lastModified: formatDate(raw.lastModified || raw.created),
  };
}
