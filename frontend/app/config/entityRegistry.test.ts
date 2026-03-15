import { describe, it, expect } from "vitest";
import {
  getEntityConfig,
  getEntityConfigByTable,
  getBasePathForCard,
  getSingularLabel,
  getLabelColorClass,
  getLabelColorClassByVariant,
  getTableName,
  mapRelationToItem,
  entityRegistry,
} from "./entityRegistry";

describe("getEntityConfig", () => {
  it("returns config for a known basePath", () => {
    const config = getEntityConfig("/court-decision");
    expect(config).toBeDefined();
    expect(config?.table).toBe("Court Decisions");
    expect(config?.singularLabel).toBe("Court Decision");
  });

  it("returns undefined for unknown basePath", () => {
    expect(getEntityConfig("/nonexistent")).toBeUndefined();
  });
});

describe("getEntityConfigByTable", () => {
  it("returns config for a known table name", () => {
    const config = getEntityConfigByTable("Court Decisions");
    expect(config).toBeDefined();
    expect(config?.singularLabel).toBe("Court Decision");
    expect(config?.variant).toBe("court-decision");
  });

  it("maps 'Answers' table to Question config", () => {
    const config = getEntityConfigByTable("Answers");
    expect(config?.singularLabel).toBe("Question");
    expect(config?.variant).toBe("question");
  });

  it("returns undefined for unknown table", () => {
    expect(getEntityConfigByTable("Unknown Table")).toBeUndefined();
  });
});

describe("getBasePathForCard", () => {
  it("resolves table name to basePath", () => {
    expect(getBasePathForCard("Court Decisions")).toBe("/court-decision");
    expect(getBasePathForCard("Answers")).toBe("/question");
    expect(getBasePathForCard("Literature")).toBe("/literature");
    expect(getBasePathForCard("Domestic Instruments")).toBe(
      "/domestic-instrument",
    );
  });

  it("resolves singular label to basePath", () => {
    expect(getBasePathForCard("Court Decision")).toBe("/court-decision");
    expect(getBasePathForCard("Question")).toBe("/question");
    expect(getBasePathForCard("Domestic Instrument")).toBe(
      "/domestic-instrument",
    );
  });

  it("returns undefined for unknown cardType", () => {
    expect(getBasePathForCard("Unknown")).toBeUndefined();
  });
});

describe("getSingularLabel", () => {
  it("returns singular label for table names", () => {
    expect(getSingularLabel("Court Decisions")).toBe("Court Decision");
    expect(getSingularLabel("Answers")).toBe("Question");
    expect(getSingularLabel("Arbitral Awards")).toBe("Arbitral Award");
  });

  it("returns singular label for already-singular input", () => {
    expect(getSingularLabel("Court Decision")).toBe("Court Decision");
    expect(getSingularLabel("Literature")).toBe("Literature");
  });

  it("returns the input string for unknown cardType", () => {
    expect(getSingularLabel("Unknown")).toBe("Unknown");
  });
});

describe("getLabelColorClass", () => {
  it("returns correct class for court decisions", () => {
    expect(getLabelColorClass("Court Decisions")).toBe("label-court-decision");
    expect(getLabelColorClass("Court Decision")).toBe("label-court-decision");
  });

  it("returns correct class for questions/answers", () => {
    expect(getLabelColorClass("Answers")).toBe("label-question");
    expect(getLabelColorClass("Question")).toBe("label-question");
  });

  it("returns correct class for instruments", () => {
    expect(getLabelColorClass("Domestic Instruments")).toBe("label-instrument");
    expect(getLabelColorClass("Regional Instrument")).toBe("label-instrument");
    expect(getLabelColorClass("International Instruments")).toBe(
      "label-instrument",
    );
  });

  it("returns correct class for arbitration entities", () => {
    expect(getLabelColorClass("Arbitral Awards")).toBe("label-arbitration");
    expect(getLabelColorClass("Arbitral Rules")).toBe("label-arbitration");
  });

  it("returns correct class for literature", () => {
    expect(getLabelColorClass("Literature")).toBe("label-literature");
  });

  it("returns hidden for jurisdiction", () => {
    expect(getLabelColorClass("Jurisdictions")).toBe("hidden");
    expect(getLabelColorClass("Jurisdiction")).toBe("hidden");
  });

  it("returns empty string for unknown cardType", () => {
    expect(getLabelColorClass("Unknown")).toBe("");
  });
});

describe("getLabelColorClassByVariant", () => {
  it("returns class for known variant", () => {
    expect(getLabelColorClassByVariant("court-decision")).toBe(
      "label-court-decision",
    );
    expect(getLabelColorClassByVariant("instrument")).toBe("label-instrument");
  });

  it("returns hidden for jurisdiction variant", () => {
    expect(getLabelColorClassByVariant("jurisdiction")).toBe("hidden");
  });

  it("returns empty string for unknown variant", () => {
    expect(getLabelColorClassByVariant("unknown")).toBe("");
    expect(getLabelColorClassByVariant("")).toBe("");
  });
});

describe("getTableName", () => {
  it("returns plural table name for singular label", () => {
    expect(getTableName("Court Decision")).toBe("Court Decisions");
    expect(getTableName("Question")).toBe("Answers");
    expect(getTableName("Domestic Instrument")).toBe("Domestic Instruments");
  });

  it("returns table name for already-plural input", () => {
    expect(getTableName("Court Decisions")).toBe("Court Decisions");
    expect(getTableName("Literature")).toBe("Literature");
  });

  it("returns the input string for unknown cardType", () => {
    expect(getTableName("Unknown")).toBe("Unknown");
  });
});

describe("searchCard configs", () => {
  it("court-decision has searchCard with PDF config", () => {
    const searchCard = entityRegistry["/court-decision"]!.searchCard!;
    expect(searchCard.fields).toHaveLength(4);
    expect(searchCard.fields[0]!.key).toBe("caseTitle");
    expect(searchCard.pdf?.folderName).toBe("court-decisions");
  });

  it("court-decision caseTitle fallback returns caseCitation", () => {
    const field = entityRegistry["/court-decision"]!.searchCard!.fields[0]!;
    expect(typeof field.fallback).toBe("function");
    const fallback = field.fallback as (
      data: Record<string, unknown>,
    ) => string;
    expect(fallback({ caseCitation: "Case 123" })).toBe("Case 123");
    expect(fallback({ caseCitation: "" })).toBe("");
  });

  it("question has searchCard without PDF config", () => {
    const searchCard = entityRegistry["/question"]!.searchCard!;
    expect(searchCard.fields).toHaveLength(3);
    expect(searchCard.pdf).toBeUndefined();
  });

  it("literature has searchCard with inlineImage on title", () => {
    const titleField = entityRegistry["/literature"]!.searchCard!.fields[0]!;
    expect(titleField.key).toBe("title");
    expect(titleField.inlineImage).toBeDefined();
    expect(titleField.inlineImage?.dataKey).toBe("openAccess");
  });

  it("literature includes both publicationTitle and publisher (hidden when empty)", () => {
    const fields = entityRegistry["/literature"]!.searchCard!.fields;
    expect(fields.find((f) => f.key === "publicationTitle")).toBeDefined();
    expect(fields.find((f) => f.key === "publisher")).toBeDefined();
  });

  it("literature has no processData (themes pass through directly)", () => {
    expect(
      entityRegistry["/literature"]!.searchCard!.processData,
    ).toBeUndefined();
  });

  it("domestic-instrument has processData that maps themes", () => {
    const searchCard = entityRegistry["/domestic-instrument"]!.searchCard!;
    const processed = searchCard.processData!({
      titleInEnglish: "Test",
      domesticLegalProvisionsThemes: "Theme A, Theme B",
    });
    expect(processed.themes).toBe("Theme A, Theme B");
  });

  it("all entities with searchCard have at least one field", () => {
    for (const [basePath, config] of Object.entries(entityRegistry)) {
      if (config.searchCard) {
        expect(
          config.searchCard.fields.length,
          `${basePath} should have at least one search card field`,
        ).toBeGreaterThan(0);
      }
    }
  });

  it("entities appearing in search results have searchCard defined", () => {
    const searchableTables = [
      "Court Decisions",
      "Answers",
      "Literature",
      "Domestic Instruments",
      "Regional Instruments",
      "International Instruments",
      "Arbitral Awards",
      "Arbitral Rules",
    ];
    for (const table of searchableTables) {
      const config = getEntityConfigByTable(table);
      expect(
        config?.searchCard,
        `${table} should have searchCard config`,
      ).toBeDefined();
    }
  });
});

describe("mapRelationToItem", () => {
  it("extracts id and title from various field names", () => {
    expect(mapRelationToItem({ coldId: "CH_001", caseTitle: "A v B" })).toEqual(
      { id: "CH_001", title: "A v B" },
    );
    expect(
      mapRelationToItem({ id: "123", titleInEnglish: "Some Law" }),
    ).toEqual({ id: "123", title: "Some Law" });
  });

  it("adds OUP badge when oupJdChapter is present", () => {
    const result = mapRelationToItem({
      id: "1",
      title: "Test",
      oupJdChapter: true,
    });
    expect(result.badge).toEqual({
      label: "OUP",
      color: "var(--color-label-oup)",
    });
  });

  it("does not add badge without oupJdChapter", () => {
    const result = mapRelationToItem({ id: "1", title: "Test" });
    expect(result.badge).toBeUndefined();
  });
});
