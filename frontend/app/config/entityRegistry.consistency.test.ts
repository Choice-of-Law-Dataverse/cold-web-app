import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { describe, it, expect } from "vitest";
import {
  entityRegistry,
  getBasePathForCollection,
  getFeedbackTypeForPath,
  getNewEntityTypes,
  RELATION_RENDERERS,
} from "./entityRegistry";
import { ENTITY_TYPE_LABELS } from "./feedback";
import { MODERATION_CATEGORIES } from "./moderationConfig";
import { SITEMAP_GROUPS } from "../../server/utils/sitemapSources";

const pagesDir = resolve(process.cwd(), "app/pages");
const hasPage = (basePath: string, file: string) =>
  existsSync(`${pagesDir}${basePath}/${file}`);

const entries = Object.entries(entityRegistry);

describe("entity registry consistency", () => {
  it.each(entries)("%s flags match the page files", (basePath, config) => {
    expect(hasPage(basePath, "[coldId].vue")).toBe(
      config.hasDetailPage !== false,
    );
    expect(hasPage(basePath, "index.vue")).toBe(config.hasIndexPage !== false);
    expect(hasPage(basePath, "new.vue")).toBe(config.hasNewPage === true);
  });

  it("uses each collection slug once", () => {
    const collections = entries.flatMap(([, c]) =>
      c.collection ? [c.collection] : [],
    );
    expect(new Set(collections).size).toBe(collections.length);
  });

  it.each(Object.entries(SITEMAP_GROUPS))(
    "sitemap group %s points at the registered entity",
    (_, group) => {
      expect(getBasePathForCollection(group.slug)).toBe(group.path);
    },
  );

  it("routes every entity moderation category to a submittable entity", () => {
    const entityCategories = MODERATION_CATEGORIES.map((c) => c.id).filter(
      (id) => id !== "case-analyzer" && id !== "feedback",
    );
    const submittable = entries
      .filter(([, c]) => c.hasNewPage)
      .map(([, c]) => c.collection);

    expect(entityCategories.sort()).toEqual([...submittable].sort());
  });

  it("labels every feedback entity type the backend accepts", () => {
    const registered = entries.flatMap(([, c]) =>
      c.feedbackType ? [c.feedbackType] : [],
    );
    expect(registered.sort()).toEqual(Object.keys(ENTITY_TYPE_LABELS).sort());
  });

  it.each(Object.entries(RELATION_RENDERERS))(
    "relation %s links to a registered entity",
    (_, renderer) => {
      expect(entityRegistry[renderer.basePath]).toBeDefined();
    },
  );

  it("derives the feedback type from a page path", () => {
    expect(getFeedbackTypeForPath("/court-decision/CD-1")).toBe(
      "court_decision",
    );
    expect(getFeedbackTypeForPath("/question/Q1")).toBe("question");
    expect(getFeedbackTypeForPath("/specialist/S1")).toBe("");
    expect(getFeedbackTypeForPath("/learn/faq")).toBe("");
  });

  it("offers a new-record option for each entity with a new page", () => {
    expect(getNewEntityTypes()).toEqual([
      "Court Decision",
      "Domestic Instrument",
      "Regional Instrument",
      "International Instrument",
      "Literature",
    ]);
  });
});
