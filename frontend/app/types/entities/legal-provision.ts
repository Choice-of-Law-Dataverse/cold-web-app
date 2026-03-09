import type { components } from "@/types/api-schema";

export type DomesticLegalProvisionResponse =
  components["schemas"]["DomesticLegalProvisionRecord"];
export type DomesticLegalProvisionDetailResponse =
  components["schemas"]["DomesticLegalProvisionDetail"];
export type RegionalLegalProvisionResponse =
  components["schemas"]["RegionalLegalProvisionRecord"];
export type RegionalLegalProvisionDetailResponse =
  components["schemas"]["RegionalLegalProvisionDetail"];
export type InternationalLegalProvisionResponse =
  components["schemas"]["InternationalLegalProvisionRecord"];
export type InternationalLegalProvisionDetailResponse =
  components["schemas"]["InternationalLegalProvisionDetail"];

export type DomesticLegalProvision = DomesticLegalProvisionDetailResponse & {
  hasEnglishTranslation: boolean;
};

export type RegionalLegalProvision = RegionalLegalProvisionDetailResponse;

export type InternationalLegalProvision =
  InternationalLegalProvisionDetailResponse;

export function processDomesticLegalProvision(
  raw: DomesticLegalProvisionDetailResponse,
): DomesticLegalProvision {
  return {
    ...raw,
    hasEnglishTranslation: Boolean(
      raw.fullTextOfTheProvisionEnglishTranslation,
    ),
  };
}

export function processRegionalLegalProvision(
  raw: RegionalLegalProvisionDetailResponse,
): RegionalLegalProvision {
  return raw;
}

export function processInternationalLegalProvision(
  raw: InternationalLegalProvisionDetailResponse,
): InternationalLegalProvision {
  return raw;
}
