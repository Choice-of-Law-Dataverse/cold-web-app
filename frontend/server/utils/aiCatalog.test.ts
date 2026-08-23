import { describe, it, expect } from "vitest";
import { buildAiCatalog } from "./aiCatalog";

const SITE = "https://cold.global";
const API = "https://api.cold.global/api/v1";

describe("buildAiCatalog", () => {
  const catalog = buildAiCatalog(SITE, API);

  it("declares a spec version and a stable host identity", () => {
    expect(catalog.specVersion).toBeTruthy();
    expect(catalog.host.identifier).toBe("did:web:cold.global");
    expect(catalog.host.displayName).toBe("Choice of Law Dataverse");
  });

  it("publishes a non-empty entries array", () => {
    expect(catalog.entries.length).toBeGreaterThan(0);
  });

  it("gives every entry the required fields", () => {
    for (const entry of catalog.entries) {
      expect(entry.identifier).toMatch(/^urn:air:cold\.global:[a-z]+:[a-z-]+$/);
      expect(entry.displayName).toBeTruthy();
      expect(entry.type).toMatch(/^[a-z]+\/[a-zA-Z0-9.+-]+$/);
    }
  });

  it("gives every entry exactly one of url or data, per spec 3.4", () => {
    for (const entry of catalog.entries) {
      const record = entry as unknown as Record<string, unknown>;
      const hasUrl = typeof record.url === "string" && record.url !== "";
      const hasData = record.data !== undefined;
      expect(hasUrl !== hasData).toBe(true);
    }
  });

  it("gives every entry 2-5 representative queries", () => {
    for (const entry of catalog.entries) {
      expect(entry.representativeQueries.length).toBeGreaterThanOrEqual(2);
      expect(entry.representativeQueries.length).toBeLessThanOrEqual(5);
    }
  });

  it("uses unique identifiers", () => {
    const ids = catalog.entries.map((entry) => entry.identifier);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("points every entry at an absolute URL", () => {
    for (const entry of catalog.entries) {
      expect(() => new URL(entry.url)).not.toThrow();
    }
  });

  it("derives the urn namespace from the configured site, not a constant", () => {
    const other = buildAiCatalog("https://staging.example.org", API);
    expect(other.host.identifier).toBe("did:web:staging.example.org");
    expect(other.entries[0]?.identifier).toContain(
      "urn:air:staging.example.org:",
    );
  });

  it("omits the API entries when no backend is configured", () => {
    const withoutApi = buildAiCatalog(SITE, undefined);
    expect(withoutApi.entries.length).toBeGreaterThan(0);
    expect(
      withoutApi.entries.every(
        (entry) => !entry.url.includes("api.cold.global"),
      ),
    ).toBe(true);
  });
});
