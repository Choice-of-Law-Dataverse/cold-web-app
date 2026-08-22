import { describe, it, expect } from "vitest";
import {
  buildApiCatalog,
  buildApiResourceUrls,
  buildLinkHeader,
} from "./agentDiscovery";

const API_BASE_URL = "https://api.cold.global/api/v1";

describe("buildApiResourceUrls", () => {
  it("derives the OpenAPI and docs URLs from the API base URL", () => {
    expect(buildApiResourceUrls(API_BASE_URL)).toEqual({
      anchor: "https://api.cold.global/api/v1",
      serviceDesc: "https://api.cold.global/api/v1/openapi.json",
      serviceDoc: "https://api.cold.global/api/v1/docs",
    });
  });

  it("ignores trailing slashes on the API base URL", () => {
    expect(buildApiResourceUrls(`${API_BASE_URL}/`).serviceDoc).toBe(
      "https://api.cold.global/api/v1/docs",
    );
  });
});

describe("buildLinkHeader", () => {
  it("advertises the api catalog, service description, docs and license", () => {
    expect(buildLinkHeader(API_BASE_URL)).toBe(
      '</.well-known/api-catalog>; rel="api-catalog"; type="application/linkset+json", ' +
        '<https://api.cold.global/api/v1/openapi.json>; rel="service-desc"; type="application/json", ' +
        '<https://api.cold.global/api/v1/docs>; rel="service-doc"; type="text/html", ' +
        '<https://creativecommons.org/licenses/by/4.0/>; rel="license"',
    );
  });

  it("omits API links when no API base URL is configured", () => {
    const header = buildLinkHeader(undefined);

    expect(header).toContain('rel="api-catalog"');
    expect(header).toContain('rel="license"');
    expect(header).not.toContain('rel="service-desc"');
    expect(header).not.toContain('rel="service-doc"');
  });
});

describe("buildApiCatalog", () => {
  it("returns an RFC 9727 linkset anchored on the API base URL", () => {
    const catalog = buildApiCatalog(API_BASE_URL);

    expect(catalog.linkset).toHaveLength(1);
    expect(catalog.linkset[0]?.anchor).toBe("https://api.cold.global/api/v1");
    expect(catalog.linkset[0]?.["service-desc"]?.[0]?.href).toBe(
      "https://api.cold.global/api/v1/openapi.json",
    );
    expect(catalog.linkset[0]?.["service-doc"]?.[0]?.href).toBe(
      "https://api.cold.global/api/v1/docs",
    );
  });

  it("returns an empty linkset when no API base URL is configured", () => {
    expect(buildApiCatalog(undefined)).toEqual({ linkset: [] });
  });
});
