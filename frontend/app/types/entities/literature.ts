/**
 * Literature entity type definitions
 */
import { formatDate } from "@/utils/format";

/** Raw API response */
export interface LiteratureResponse {
  id: string;
  sourceTable?: string;
  recordId?: string;
  coldId?: string;
  ID?: string;
  Key?: string;
  itemType?: string;
  publicationYear?: string;
  Author?: string;
  Title?: string;
  ISBN?: string;
  ISSN?: string;
  Url?: string;
  Date?: string;
  dateAdded?: string;
  dateModified?: string;
  Publisher?: string;
  Language?: string;
  Extra?: string;
  manualTags?: string;
  Editor?: string;
  lastModified?: string;
  Created?: string;
  publicationTitle?: string;
  Issue?: string;
  Volume?: string;
  Pages?: string;
  abstractNote?: string;
  libraryCatalog?: string;
  DOI?: string;
  accessDate?: string;
  openAccess?: string;
  openAccessUrl?: string;
  journalAbbreviation?: string;
  shortTitle?: string;
  Place?: string;
  numPages?: string;
  Type?: string;
  oupJdChapter?: string;
  Contributor?: string;
  automaticTags?: string;
  Number?: string;
  Series?: string;
  seriesNumber?: string;
  seriesEditor?: string;
  Edition?: string;
  callNumber?: string;
  jurisdictionSummary?: string;
  Answers?: string;
  sortDate?: string;
  jurisdictionLink?: string;
  Jurisdiction?: string;
  themes?: string;
  themesLink?: string;
  internationalInstruments?: string;
  internationalInstrumentsLink?: string;
  internationalLegalProvisions?: string;
  internationalLegalProvisionsLink?: string;
  regionalInstruments?: string;
  regionalInstrumentsLink?: string;
  officialSourcePdf?: string;
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
    isOupChapter: Boolean(raw.oupJdChapter),
    lastModified: formatDate(raw.lastModified || raw.Created),
  };
}
