/**
 * Literature entity type definitions
 */
import { formatDate } from "@/utils/format";

/** Raw API response */
export interface LiteratureResponse {
  id: string;
  source_table?: string;
  "Record ID"?: string;
  CoLD_ID?: string;
  ID?: string;
  Key?: string;
  "Item Type"?: string;
  "Publication Year"?: string;
  Author?: string;
  Title?: string;
  ISBN?: string;
  ISSN?: string;
  Url?: string;
  Date?: string;
  "Date Added"?: string;
  "Date Modified"?: string;
  Publisher?: string;
  Language?: string;
  Extra?: string;
  "Manual Tags"?: string;
  Editor?: string;
  "Last Modified"?: string;
  Created?: string;
  "Publication Title"?: string;
  Issue?: string;
  Volume?: string;
  Pages?: string;
  "Abstract Note"?: string;
  "Library Catalog"?: string;
  DOI?: string;
  "Access Date"?: string;
  "Open Access"?: string;
  "Open Access URL"?: string;
  "Journal Abbreviation"?: string;
  "Short Title"?: string;
  Place?: string;
  "Num Pages"?: string;
  Type?: string;
  "OUP JD Chapter"?: string;
  Contributor?: string;
  "Automatic Tags"?: string;
  Number?: string;
  Series?: string;
  "Series Number"?: string;
  "Series Editor"?: string;
  Edition?: string;
  "Call Number"?: string;
  "Jurisdiction Summary"?: string;
  Answers?: string;
  sort_date?: string;
  // Nested mappings
  "Jurisdiction Link"?: string;
  Jurisdiction?: string;
  Themes?: string;
  "Themes Link"?: string;
  "International Instruments"?: string;
  "International Instruments Link"?: string;
  "International Legal Provisions"?: string;
  "International Legal Provisions Link"?: string;
  "Regional Instruments"?: string;
  "Regional Instruments Link"?: string;
  // Legacy/additional fields
  "Official Source (PDF)"?: string;
}

/** Processed type with normalized fields */
export interface Literature extends LiteratureResponse {
  /** Pre-computed display title */
  displayTitle: string;
  /** Whether this is an OUP JD Chapter */
  isOupChapter: boolean;
}

/** Transform raw response to processed type */
export function processLiterature(raw: LiteratureResponse): Literature {
  return {
    ...raw,
    displayTitle: raw.Title || "Untitled",
    isOupChapter: Boolean(raw["OUP JD Chapter"]),
    "Last Modified": formatDate(raw["Last Modified"] || raw.Created),
  };
}
