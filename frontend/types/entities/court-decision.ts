/**
 * Court Decision entity type definitions
 */

export interface CourtDecisionResponse {
  id: string;
  "Case Title"?: string;
  "Case Citation"?: string;
  "Publication Date ISO"?: string;
  "Date of Judgment"?: string;
  Instance?: string;
  Abstract?: string;
  "Relevant Facts"?: string;
  "PIL Provisions"?: string;
  "Domestic Legal Provisions"?: string;
  "Text of the Relevant Legal Provisions"?: string;
  "Choice of Law Issue"?: string;
  "Court's Position"?: string;
  Quote?: string;
  "Translated Excerpt"?: string;
  hasEnglishQuoteTranslation?: boolean;
  "Original Text"?: string;
  "Related Questions"?: string;
  "Related Literature"?: string;
  "OUP Chapter"?: string;
  "Country Report"?: string;
  "Official Source (PDF)"?: string;
  "Official Source (URL)"?: string;
  "Jurisdictions Alpha-3 Code"?: string;
  themes?: string;
}
