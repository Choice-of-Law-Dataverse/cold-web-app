import { describe, it, expect } from "vitest";
import { SITEMAP_GROUPS, toSitemapLocations } from "./sitemapSources";

describe("SITEMAP_GROUPS", () => {
  it("covers every entity type that has a detail page", () => {
    expect(Object.keys(SITEMAP_GROUPS).sort()).toEqual([
      "arbitral-awards",
      "arbitral-institutions",
      "arbitral-rules",
      "court-decisions",
      "domestic-instruments",
      "international-instruments",
      "jurisdictions",
      "literature",
      "questions",
      "regional-instruments",
      "specialists",
    ]);
  });

  it("points questions at the comparative route, not the answer route", () => {
    expect(SITEMAP_GROUPS.questions?.slug).toBe("questions");
    expect(SITEMAP_GROUPS.questions?.path).toBe("/question");
  });
});

describe("toSitemapLocations", () => {
  const group = SITEMAP_GROUPS["court-decisions"]!;

  it("builds detail routes from coldIds", () => {
    expect(
      toSitemapLocations(group, [{ coldId: "CD-ISR-524" }, { coldId: "CD-1" }]),
    ).toEqual(["/court-decision/CD-ISR-524", "/court-decision/CD-1"]);
  });

  it("skips records with no coldId rather than emitting a 404 URL", () => {
    expect(
      toSitemapLocations(group, [{ coldId: null }, { coldId: "  " }, {}]),
    ).toEqual([]);
  });

  it("escapes ids that would otherwise break the URL", () => {
    expect(toSitemapLocations(group, [{ coldId: "CD ISR/1" }])).toEqual([
      "/court-decision/CD%20ISR%2F1",
    ]);
  });
});
