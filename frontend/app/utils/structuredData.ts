import { stripMarkup, toAbsoluteUrl, truncate } from "@/utils/seo";

export type JsonLdNode = Record<string, unknown>;

export const SCHEMA_CONTEXT = "https://schema.org";

const LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/";
const ORGANIZATION_ID = "#organization";
const WEBSITE_ID = "#website";
const ABSTRACT_MAX_LENGTH = 500;

/**
 * Drops keys whose value is empty so the emitted graph carries no
 * `null`/`""` noise, which validators flag and crawlers ignore anyway.
 */
export function compact(node: JsonLdNode): JsonLdNode {
  const result: JsonLdNode = {};

  for (const [key, value] of Object.entries(node)) {
    if (value === null || value === undefined || value === "") continue;
    if (Array.isArray(value) && value.length === 0) continue;
    result[key] = value;
  }

  return result;
}

function text(
  value: string | null | undefined,
  maxLength = ABSTRACT_MAX_LENGTH,
): string | undefined {
  const cleaned = stripMarkup(value);
  return cleaned ? truncate(cleaned, maxLength) : undefined;
}

/** Wraps nodes in a single `@graph` document, the form Google prefers. */
export function buildJsonLdGraph(nodes: (JsonLdNode | null | undefined)[]) {
  const graph = nodes.filter((node): node is JsonLdNode => Boolean(node));
  return { "@context": SCHEMA_CONTEXT, "@graph": graph };
}

export function buildOrganization(siteUrl: string): JsonLdNode {
  return compact({
    "@type": "Organization",
    "@id": toAbsoluteUrl(siteUrl, "/") + ORGANIZATION_ID,
    name: "Choice of Law Dataverse",
    alternateName: "CoLD",
    url: toAbsoluteUrl(siteUrl, "/"),
    description:
      "An open research database on choice of law in international commercial contracts.",
    funder: {
      "@type": "Organization",
      name: "Swiss National Science Foundation",
      url: "https://www.snf.ch/",
    },
  });
}

export function buildWebSite(siteUrl: string): JsonLdNode {
  return compact({
    "@type": "WebSite",
    "@id": toAbsoluteUrl(siteUrl, "/") + WEBSITE_ID,
    name: "Choice of Law Dataverse",
    url: toAbsoluteUrl(siteUrl, "/"),
    inLanguage: "en",
    publisher: { "@id": toAbsoluteUrl(siteUrl, "/") + ORGANIZATION_ID },
    license: LICENSE_URL,
  });
}

/**
 * Describes the database itself so it can surface in Google Dataset Search,
 * which is the discovery surface academic users actually reach for.
 */
export function buildDataset(
  siteUrl: string,
  options: { name?: string; description?: string; path?: string } = {},
): JsonLdNode {
  const path = options.path ?? "/";
  return compact({
    "@type": "Dataset",
    "@id": toAbsoluteUrl(siteUrl, path) + "#dataset",
    name: options.name ?? "Choice of Law Dataverse",
    description:
      options.description ??
      "Court decisions, domestic and international instruments, arbitral awards and jurisdiction reports on choice of law in international commercial contracts.",
    url: toAbsoluteUrl(siteUrl, path),
    license: LICENSE_URL,
    isAccessibleForFree: true,
    creator: { "@id": toAbsoluteUrl(siteUrl, "/") + ORGANIZATION_ID },
    publisher: { "@id": toAbsoluteUrl(siteUrl, "/") + ORGANIZATION_ID },
    keywords: [
      "choice of law",
      "private international law",
      "conflict of laws",
      "international commercial contracts",
      "party autonomy",
      "international arbitration",
    ],
  });
}

export interface BreadcrumbItem {
  name: string;
  path: string;
}

export function buildBreadcrumbList(
  siteUrl: string,
  items: BreadcrumbItem[],
): JsonLdNode | null {
  const usable = items.filter((item) => Boolean(stripMarkup(item.name)));
  if (usable.length < 2) return null;

  return {
    "@type": "BreadcrumbList",
    itemListElement: usable.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: stripMarkup(item.name),
      item: toAbsoluteUrl(siteUrl, item.path),
    })),
  };
}

function jurisdictionNames(
  relations: { jurisdictions?: { name?: string | null }[] } | undefined,
): string[] {
  return (relations?.jurisdictions ?? [])
    .map((jurisdiction) => stripMarkup(jurisdiction?.name))
    .filter(Boolean);
}

export interface CourtDecisionLike {
  caseTitle?: string | null;
  caseCitation?: string | null;
  publicationDateIso?: string | null;
  dateOfJudgment?: string | null;
  instance?: string | null;
  abstract?: string | null;
  choiceOfLawIssue?: string | null;
  relations?: { jurisdictions?: { name?: string | null }[] };
}

export function buildCourtDecisionNode(
  siteUrl: string,
  path: string,
  data: CourtDecisionLike,
): JsonLdNode {
  const jurisdictions = jurisdictionNames(data.relations);

  return compact({
    "@type": "Report",
    "@id": toAbsoluteUrl(siteUrl, path) + "#record",
    name: text(data.caseTitle ?? data.caseCitation, 200),
    headline: text(data.caseTitle ?? data.caseCitation, 200),
    url: toAbsoluteUrl(siteUrl, path),
    abstract: text(data.abstract ?? data.choiceOfLawIssue),
    datePublished: data.publicationDateIso ?? data.dateOfJudgment ?? undefined,
    citation: text(data.caseCitation, 300),
    genre: "Court decision",
    inLanguage: "en",
    license: LICENSE_URL,
    isPartOf: { "@id": toAbsoluteUrl(siteUrl, "/") + "#dataset" },
    publisher: { "@id": toAbsoluteUrl(siteUrl, "/") + ORGANIZATION_ID },
    about: jurisdictions.map((name) => ({ "@type": "Place", name })),
    spatialCoverage: jurisdictions.map((name) => ({ "@type": "Place", name })),
    producer: data.instance
      ? { "@type": "GovernmentOrganization", name: stripMarkup(data.instance) }
      : undefined,
  });
}

export interface LegislationLike {
  title?: string | null;
  name?: string | null;
  titleInEnglish?: string | null;
  officialTitle?: string | null;
  abbreviation?: string | null;
  date?: string | null;
  entryIntoForce?: string | null;
  sourceUrl?: string | null;
  url?: string | null;
  relations?: { jurisdictions?: { name?: string | null }[] };
}

export function buildLegislationNode(
  siteUrl: string,
  path: string,
  data: LegislationLike,
): JsonLdNode {
  const title =
    data.titleInEnglish ?? data.title ?? data.name ?? data.officialTitle;

  return compact({
    "@type": "Legislation",
    "@id": toAbsoluteUrl(siteUrl, path) + "#record",
    name: text(title, 200),
    alternateName: text(data.officialTitle ?? data.abbreviation, 200),
    url: toAbsoluteUrl(siteUrl, path),
    legislationDate: data.date ?? undefined,
    temporalCoverage: data.entryIntoForce ?? undefined,
    inLanguage: "en",
    license: LICENSE_URL,
    sameAs: data.sourceUrl ?? data.url ?? undefined,
    isPartOf: { "@id": toAbsoluteUrl(siteUrl, "/") + "#dataset" },
    jurisdiction: jurisdictionNames(data.relations).map((name) => ({
      "@type": "AdministrativeArea",
      name,
    })),
  });
}

export interface LiteratureLike {
  title?: string | null;
  author?: string | null;
  publicationYear?: string | number | null;
  publicationTitle?: string | null;
  publisher?: string | null;
  abstractNote?: string | null;
  doi?: string | null;
  isbn?: string | null;
  issn?: string | null;
  openAccessUrl?: string | null;
  pages?: string | null;
  itemType?: string | null;
}

export function buildLiteratureNode(
  siteUrl: string,
  path: string,
  data: LiteratureLike,
): JsonLdNode {
  const authors = stripMarkup(data.author)
    .split(/;|\band\b/)
    .map((name) => name.trim())
    .filter(Boolean)
    .map((name) => ({ "@type": "Person", name }));

  return compact({
    "@type": "ScholarlyArticle",
    "@id": toAbsoluteUrl(siteUrl, path) + "#record",
    name: text(data.title, 250),
    headline: text(data.title, 250),
    url: toAbsoluteUrl(siteUrl, path),
    abstract: text(data.abstractNote),
    author: authors,
    datePublished: data.publicationYear
      ? String(data.publicationYear)
      : undefined,
    isPartOf: data.publicationTitle
      ? { "@type": "Periodical", name: stripMarkup(data.publicationTitle) }
      : undefined,
    publisher: data.publisher
      ? { "@type": "Organization", name: stripMarkup(data.publisher) }
      : undefined,
    pagination: data.pages ?? undefined,
    isbn: data.isbn ?? undefined,
    issn: data.issn ?? undefined,
    sameAs: data.doi ? `https://doi.org/${data.doi}` : undefined,
    identifier: data.doi ?? undefined,
  });
}

export interface JurisdictionLike {
  name?: string | null;
  region?: string | null;
  legalFamily?: string | null;
  jurisdictionSummary?: string | null;
}

export function buildJurisdictionNode(
  siteUrl: string,
  path: string,
  data: JurisdictionLike,
): JsonLdNode {
  return compact({
    "@type": "Article",
    "@id": toAbsoluteUrl(siteUrl, path) + "#record",
    name: text(data.name ? `${data.name} — choice of law report` : null, 200),
    headline: text(data.name ? `Choice of law in ${data.name}` : null, 200),
    url: toAbsoluteUrl(siteUrl, path),
    abstract: text(data.jurisdictionSummary),
    inLanguage: "en",
    license: LICENSE_URL,
    isPartOf: { "@id": toAbsoluteUrl(siteUrl, "/") + "#dataset" },
    publisher: { "@id": toAbsoluteUrl(siteUrl, "/") + ORGANIZATION_ID },
    about: data.name
      ? {
          "@type": "AdministrativeArea",
          name: stripMarkup(data.name),
          additionalProperty: compact({
            "@type": "PropertyValue",
            name: "Legal family",
            value: stripMarkup(data.legalFamily),
          }),
        }
      : undefined,
    spatialCoverage: data.region
      ? { "@type": "Place", name: stripMarkup(data.region) }
      : undefined,
  });
}

export interface SpecialistLike {
  specialist?: string | null;
  affiliation?: string | null;
  bio?: string | null;
  website?: string | null;
}

export function buildSpecialistNode(
  siteUrl: string,
  path: string,
  data: SpecialistLike,
): JsonLdNode {
  return compact({
    "@type": "Person",
    "@id": toAbsoluteUrl(siteUrl, path) + "#record",
    name: text(data.specialist, 120),
    url: toAbsoluteUrl(siteUrl, path),
    description: text(data.bio),
    sameAs: data.website ?? undefined,
    affiliation: data.affiliation
      ? { "@type": "Organization", name: stripMarkup(data.affiliation) }
      : undefined,
  });
}

export interface ArbitralInstitutionLike {
  institution?: string | null;
  abbreviation?: string | null;
}

export function buildArbitralInstitutionNode(
  siteUrl: string,
  path: string,
  data: ArbitralInstitutionLike,
): JsonLdNode {
  return compact({
    "@type": "Organization",
    "@id": toAbsoluteUrl(siteUrl, path) + "#record",
    name: text(data.institution, 200),
    alternateName: text(data.abbreviation, 60),
    url: toAbsoluteUrl(siteUrl, path),
  });
}

export interface ArbitralAwardLike {
  caseNumber?: string | null;
  year?: string | number | null;
  seatTown?: string | null;
  awardSummary?: string | null;
  natureOfTheAward?: string | null;
}

export function buildArbitralAwardNode(
  siteUrl: string,
  path: string,
  data: ArbitralAwardLike,
): JsonLdNode {
  return compact({
    "@type": "Report",
    "@id": toAbsoluteUrl(siteUrl, path) + "#record",
    name: text(
      data.caseNumber ? `Arbitral award ${data.caseNumber}` : null,
      200,
    ),
    url: toAbsoluteUrl(siteUrl, path),
    abstract: text(data.awardSummary ?? data.natureOfTheAward),
    datePublished: data.year ? String(data.year) : undefined,
    genre: "Arbitral award",
    inLanguage: "en",
    license: LICENSE_URL,
    isPartOf: { "@id": toAbsoluteUrl(siteUrl, "/") + "#dataset" },
    spatialCoverage: data.seatTown
      ? { "@type": "Place", name: stripMarkup(data.seatTown) }
      : undefined,
  });
}

export interface ArbitralRuleLike {
  setOfRules?: string | null;
  inForceFrom?: string | null;
  officialSourceUrl?: string | null;
}

export function buildArbitralRuleNode(
  siteUrl: string,
  path: string,
  data: ArbitralRuleLike,
): JsonLdNode {
  return compact({
    "@type": "Legislation",
    "@id": toAbsoluteUrl(siteUrl, path) + "#record",
    name: text(data.setOfRules, 200),
    url: toAbsoluteUrl(siteUrl, path),
    legislationDate: data.inForceFrom ?? undefined,
    sameAs: data.officialSourceUrl ?? undefined,
    inLanguage: "en",
    isPartOf: { "@id": toAbsoluteUrl(siteUrl, "/") + "#dataset" },
  });
}

export interface FaqEntry {
  question: string;
  answer: string;
}

export function buildFaqPage(entries: FaqEntry[]): JsonLdNode | null {
  const usable = entries
    .map((entry) => ({
      question: stripMarkup(entry.question),
      answer: stripMarkup(entry.answer),
    }))
    .filter((entry) => entry.question && entry.answer);

  if (usable.length === 0) return null;

  return {
    "@type": "FAQPage",
    mainEntity: usable.map((entry) => ({
      "@type": "Question",
      name: entry.question,
      acceptedAnswer: { "@type": "Answer", text: entry.answer },
    })),
  };
}

export interface GlossaryTerm {
  term: string;
  definition: string;
}

export function buildDefinedTermSet(
  siteUrl: string,
  path: string,
  terms: GlossaryTerm[],
): JsonLdNode | null {
  const usable = terms
    .map((entry) => ({
      term: stripMarkup(entry.term),
      definition: stripMarkup(entry.definition),
    }))
    .filter((entry) => entry.term && entry.definition);

  if (usable.length === 0) return null;

  const setId = toAbsoluteUrl(siteUrl, path) + "#glossary";

  return {
    "@type": "DefinedTermSet",
    "@id": setId,
    name: "CoLD Glossary",
    url: toAbsoluteUrl(siteUrl, path),
    hasDefinedTerm: usable.map((entry) => ({
      "@type": "DefinedTerm",
      name: entry.term,
      description: entry.definition,
      inDefinedTermSet: { "@id": setId },
    })),
  };
}
