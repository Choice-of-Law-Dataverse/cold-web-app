import { joinURL } from "ufo";

const LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/";

/** ai-catalog data model version, not the ARD spec version. */
const SPEC_VERSION = "1.0";

export const AI_CATALOG_PATH = "/.well-known/ai-catalog.json";

export interface AiCatalogEntry {
  identifier: string;
  displayName: string;
  description: string;
  type: string;
  url: string;
  representativeQueries: string[];
}

export interface AiCatalog {
  specVersion: string;
  host: {
    displayName: string;
    identifier: string;
    description: string;
    url: string;
    license: string;
  };
  entries: AiCatalogEntry[];
}

function hostname(siteUrl: string): string {
  try {
    return new URL(siteUrl).hostname;
  } catch {
    return "cold.global";
  }
}

/**
 * ARD capability manifest describing what an agent can do with CoLD.
 *
 * Every entry carries exactly one of `url` or `data` as the spec requires, and
 * 2-5 `representativeQueries` so registries can build semantic embeddings from
 * the kind of question each resource actually answers.
 *
 * @see https://agenticresourcediscovery.org/
 */
export function buildAiCatalog(
  siteUrl: string,
  apiBaseUrl: string | undefined,
): AiCatalog {
  const site = String(siteUrl || "").replace(/\/+$/, "");
  const fqdn = hostname(site);
  const api = String(apiBaseUrl || "").replace(/\/+$/, "");
  const urn = (namespace: string, name: string) =>
    `urn:air:${fqdn}:${namespace}:${name}`;

  const entries: AiCatalogEntry[] = [
    {
      identifier: urn("doc", "llms-txt"),
      displayName: "CoLD for language models",
      description:
        "Curated index of the Choice of Law Dataverse: what it covers, how to query it, and how to cite it.",
      type: "text/markdown",
      url: joinURL(site, "/llms.txt"),
      representativeQueries: [
        "what is the Choice of Law Dataverse",
        "how do I cite CoLD",
        "what data does cold.global publish",
      ],
    },
  ];

  if (api) {
    entries.push(
      {
        identifier: urn("api", "cold-api"),
        displayName: "CoLD API",
        description:
          "OpenAPI description of the public, unauthenticated read API for every CoLD dataset.",
        type: "application/vnd.oai.openapi+json",
        url: joinURL(api, "openapi.json"),
        representativeQueries: [
          "what endpoints does the CoLD API expose",
          "how do I fetch a court decision as JSON",
          "is there an API for choice of law data",
        ],
      },
      {
        identifier: urn("tool", "search"),
        displayName: "Full-text search across CoLD",
        description:
          "Search court decisions, instruments, arbitral awards, literature and jurisdiction reports in one query.",
        type: "application/json",
        url: joinURL(api, "search/"),
        representativeQueries: [
          "find court decisions about party autonomy in Brazil",
          "search CoLD for the public policy exception",
          "which cases cite the HCCH Principles",
        ],
      },
      {
        identifier: urn("tool", "entities"),
        displayName: "CoLD entity collections",
        description:
          "Paginated lists per entity type: court decisions, jurisdictions, instruments, arbitral awards, literature and specialists.",
        type: "application/json",
        url: joinURL(api, "entities/court-decisions"),
        representativeQueries: [
          "list every jurisdiction covered by CoLD",
          "how many court decisions are in the dataset",
          "enumerate the domestic choice of law instruments",
        ],
      },
      {
        identifier: urn("tool", "statistics"),
        displayName: "CoLD dataset statistics",
        description:
          "Record counts per entity type and jurisdiction-level answer coverage.",
        type: "application/json",
        url: joinURL(api, "statistics/counts"),
        representativeQueries: [
          "how large is the Choice of Law Dataverse",
          "how many jurisdictions have choice of law reports",
        ],
      },
    );
  }

  entries.push({
    identifier: urn("index", "sitemap"),
    displayName: "CoLD sitemap index",
    description:
      "Every indexable CoLD URL, split by entity type, for agents that prefer crawling pages to calling the API.",
    type: "application/xml",
    url: joinURL(site, "/sitemap_index.xml"),
    representativeQueries: [
      "list all pages on cold.global",
      "where can I find every court decision URL",
    ],
  });

  return {
    specVersion: SPEC_VERSION,
    host: {
      displayName: "Choice of Law Dataverse",
      identifier: `did:web:${fqdn}`,
      description:
        "An open research database on choice of law in international commercial contracts, covering more than 200 jurisdictions.",
      url: joinURL(site, "/"),
      license: LICENSE_URL,
    },
    entries,
  };
}
