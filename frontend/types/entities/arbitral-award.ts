/**
 * Arbitral Award entity type definitions
 */

export interface ArbitralAwardResponse {
  id: string;
  "Case Number"?: string;
  "Arbitral Institutions"?: string;
  Source?: string;
  Year?: string;
  "Nature of the Award"?: string;
  Context?: string;
  "Seat (Town)"?: string;
  "Award Summary"?: string;
  related_arbitral_institutions?: Array<{ Institution?: string }>;
  related_jurisdictions?: Array<{ Name?: string }>;
  related_themes?: Array<{ Theme?: string }>;
}
