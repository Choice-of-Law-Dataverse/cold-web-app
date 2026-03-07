import { formatDate } from "@/utils/format";

export interface RegionalInstrumentResponse {
  id: string;
  sourceTable?: string;
  rank?: number;
  ID?: string;
  idNumber?: string;
  Title?: string;
  Abbreviation?: string;
  Date?: string;
  URL?: string;
  Attachment?: string;
  recordId?: string;
  Created?: string;
  lastModified?: string;
  sortDate?: string;
  Specialists?: string;
  specialistsLink?: string;
  regionalLegalProvisions?: string;
  regionalLegalProvisionsLink?: string;
  titleInEnglish?: string;
  Name?: string;
  Literature?: string;
  oupChapter?: string;
  Link?: string;
}

export interface RegionalInstrument extends RegionalInstrumentResponse {
  titleInEnglish: string;
  URL: string;
}

export function processRegionalInstrument(
  raw: RegionalInstrumentResponse,
): RegionalInstrument {
  return {
    ...raw,
    titleInEnglish: raw.titleInEnglish || raw.Name || "",
    lastModified: formatDate(raw.lastModified || raw.Created),
    Date: formatDate(raw.Date),
    URL: raw.URL || raw.Link || "",
  };
}
