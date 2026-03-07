/**
 * International Instrument entity type definitions
 */

import { formatDate } from "@/utils/format";

/** Raw API response */
export interface InternationalInstrumentResponse {
  id: string;
  sourceTable?: string;
  rank?: number;
  ID?: string;
  idNumber?: string;
  Title?: string;
  Abbreviation?: string;
  Date?: string;
  Status?: string;
  URL?: string;
  Attachment?: string;
  recordId?: string;
  Created?: string;
  lastModified?: string;
  entryIntoForce?: string;
  publicationDate?: string;
  relevantProvisions?: string;
  fullTextOfTheProvisions?: string;
  Name?: string;
  sortDate?: string;
  titleInEnglish?: string;
  sourceUrl?: string;
  sourcePdf?: string;
  Specialists?: string;
  specialistsLink?: string;
  internationalLegalProvisions?: string;
  internationalLegalProvisionsLink?: string;
  Literature?: string;
  literatureLink?: string;
  hcchAnswers?: string;
  hcchAnswersLink?: string;
  Link?: string;
  oupChapter?: string;
  selectedProvisions?: string;
}

export interface InternationalInstrument extends InternationalInstrumentResponse {
  titleInEnglish: string;
  URL: string;
}

export function processInternationalInstrument(
  raw: InternationalInstrumentResponse,
): InternationalInstrument {
  return {
    ...raw,
    publicationDate: formatDate(raw.publicationDate || raw.Date),
    titleInEnglish: raw.titleInEnglish || raw.Name || "",
    URL: raw.URL || raw.Link || "",
  };
}
