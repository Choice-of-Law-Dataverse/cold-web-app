import { joinURL } from "ufo";

const LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/";
const API_CATALOG_PATH = "/.well-known/api-catalog";
const LINKSET_TYPE = "application/linkset+json";

export interface LinkTarget {
  href: string;
  type?: string;
  title?: string;
}

export interface ApiCatalog {
  linkset: Array<{
    anchor: string;
    "service-desc"?: LinkTarget[];
    "service-doc"?: LinkTarget[];
    license?: LinkTarget[];
  }>;
}

/**
 * Absolute URLs of the machine-readable resources derived from the API base URL.
 */
export function buildApiResourceUrls(apiBaseUrl: string) {
  const base = apiBaseUrl.replace(/\/+$/, "");

  return {
    anchor: base,
    serviceDesc: joinURL(base, "openapi.json"),
    serviceDoc: joinURL(base, "docs"),
  };
}

/**
 * RFC 8288 `Link` field value advertising agent-discoverable resources.
 */
export function buildLinkHeader(apiBaseUrl: string | undefined): string {
  const links = [
    `<${API_CATALOG_PATH}>; rel="api-catalog"; type="${LINKSET_TYPE}"`,
  ];

  if (apiBaseUrl) {
    const { serviceDesc, serviceDoc } = buildApiResourceUrls(apiBaseUrl);
    links.push(
      `<${serviceDesc}>; rel="service-desc"; type="application/json"`,
      `<${serviceDoc}>; rel="service-doc"; type="text/html"`,
    );
  }

  links.push(`<${LICENSE_URL}>; rel="license"`);

  return links.join(", ");
}

/**
 * RFC 9727 API catalog document listing the public CoLD API.
 */
export function buildApiCatalog(apiBaseUrl: string | undefined): ApiCatalog {
  if (!apiBaseUrl) {
    return { linkset: [] };
  }

  const { anchor, serviceDesc, serviceDoc } = buildApiResourceUrls(apiBaseUrl);

  return {
    linkset: [
      {
        anchor,
        "service-desc": [
          {
            href: serviceDesc,
            type: "application/json",
            title: "CoLD API OpenAPI description",
          },
        ],
        "service-doc": [
          {
            href: serviceDoc,
            type: "text/html",
            title: "CoLD API reference documentation",
          },
        ],
        license: [{ href: LICENSE_URL, title: "CC BY 4.0" }],
      },
    ],
  };
}
