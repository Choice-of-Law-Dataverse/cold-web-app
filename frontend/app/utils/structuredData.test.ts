import { describe, it, expect } from "vitest";
import {
  buildArbitralAwardNode,
  buildBreadcrumbList,
  buildCourtDecisionNode,
  buildDataset,
  buildDefinedTermSet,
  buildFaqPage,
  buildJsonLdGraph,
  buildJurisdictionNode,
  buildLegislationNode,
  buildLiteratureNode,
  buildOrganization,
  buildSpecialistNode,
  compact,
  SCHEMA_CONTEXT,
} from "./structuredData";

const SITE = "https://cold.global";

describe("compact", () => {
  it("drops empty values so validators see no null noise", () => {
    expect(
      compact({ a: "x", b: null, c: undefined, d: "", e: [], f: 0, g: false }),
    ).toEqual({ a: "x", f: 0, g: false });
  });
});

describe("buildJsonLdGraph", () => {
  it("wraps nodes in a single context and skips blanks", () => {
    const graph = buildJsonLdGraph([{ "@type": "Thing" }, null, undefined]);
    expect(graph["@context"]).toBe(SCHEMA_CONTEXT);
    expect(graph["@graph"]).toHaveLength(1);
  });
});

describe("buildBreadcrumbList", () => {
  it("numbers items from one and makes each item absolute", () => {
    const node = buildBreadcrumbList(SITE, [
      { name: "Home", path: "/" },
      { name: "Literature", path: "/literature" },
    ]);
    expect(node).toEqual({
      "@type": "BreadcrumbList",
      itemListElement: [
        {
          "@type": "ListItem",
          position: 1,
          name: "Home",
          item: "https://cold.global/",
        },
        {
          "@type": "ListItem",
          position: 2,
          name: "Literature",
          item: "https://cold.global/literature",
        },
      ],
    });
  });

  it("returns null for a single-item trail, which Google rejects", () => {
    expect(buildBreadcrumbList(SITE, [{ name: "Home", path: "/" }])).toBeNull();
  });
});

describe("buildCourtDecisionNode", () => {
  it("emits a Report with citation, date and jurisdiction", () => {
    const node = buildCourtDecisionNode(SITE, "/court-decision/CD-ISR-524", {
      caseTitle: "Klausner v Berkovitz",
      caseCitation: "CA 750/79",
      publicationDateIso: "1983-11-20",
      instance: "Court of Appeal",
      abstract: "<p>Party autonomy</p>",
      relations: { jurisdictions: [{ name: "Israel" }] },
    });

    expect(node["@type"]).toBe("Report");
    expect(node.name).toBe("Klausner v Berkovitz");
    expect(node.datePublished).toBe("1983-11-20");
    expect(node.abstract).toBe("Party autonomy");
    expect(node.citation).toBe("CA 750/79");
    expect(node.spatialCoverage).toEqual([
      { "@type": "Place", name: "Israel" },
    ]);
  });

  it("falls back to the citation when there is no case title", () => {
    const node = buildCourtDecisionNode(SITE, "/court-decision/X", {
      caseCitation: "CA 1/23",
    });
    expect(node.name).toBe("CA 1/23");
  });

  it("omits keys the record has no data for", () => {
    const node = buildCourtDecisionNode(SITE, "/court-decision/X", {});
    expect(node).not.toHaveProperty("datePublished");
    expect(node).not.toHaveProperty("abstract");
    expect(node).not.toHaveProperty("producer");
  });
});

describe("buildLegislationNode", () => {
  it("prefers the English title and links the official source", () => {
    const node = buildLegislationNode(SITE, "/domestic-instrument/DI-1", {
      titleInEnglish: "Contracts Act",
      officialTitle: "Loi sur les contrats",
      date: "1987-01-01",
      sourceUrl: "https://example.gov/act",
      relations: { jurisdictions: [{ name: "Switzerland" }] },
    });

    expect(node["@type"]).toBe("Legislation");
    expect(node.name).toBe("Contracts Act");
    expect(node.alternateName).toBe("Loi sur les contrats");
    expect(node.legislationDate).toBe("1987-01-01");
    expect(node.sameAs).toBe("https://example.gov/act");
    expect(node.jurisdiction).toEqual([
      { "@type": "AdministrativeArea", name: "Switzerland" },
    ]);
  });
});

describe("buildLiteratureNode", () => {
  it("splits authors and turns a DOI into a resolvable URL", () => {
    const node = buildLiteratureNode(SITE, "/literature/L-1", {
      title: "Party Autonomy",
      author: "Smith, J; Doe, A",
      publicationYear: 2019,
      doi: "10.1000/xyz",
    });

    expect(node["@type"]).toBe("ScholarlyArticle");
    expect(node.author).toEqual([
      { "@type": "Person", name: "Smith, J" },
      { "@type": "Person", name: "Doe, A" },
    ]);
    expect(node.datePublished).toBe("2019");
    expect(node.sameAs).toBe("https://doi.org/10.1000/xyz");
  });
});

describe("buildJurisdictionNode", () => {
  it("frames the report around the jurisdiction name", () => {
    const node = buildJurisdictionNode(SITE, "/jurisdiction/CHE", {
      name: "Switzerland",
      region: "Europe",
      legalFamily: "Civil law",
      jurisdictionSummary: "Swiss law permits choice of law.",
    });

    expect(node.headline).toBe("Choice of law in Switzerland");
    expect(node.abstract).toBe("Swiss law permits choice of law.");
    expect(node.spatialCoverage).toEqual({ "@type": "Place", name: "Europe" });
  });
});

describe("buildSpecialistNode and buildArbitralAwardNode", () => {
  it("emits a Person with affiliation", () => {
    const node = buildSpecialistNode(SITE, "/specialist/S-1", {
      specialist: "Jane Roe",
      affiliation: "University of Lucerne",
    });
    expect(node["@type"]).toBe("Person");
    expect(node.affiliation).toEqual({
      "@type": "Organization",
      name: "University of Lucerne",
    });
  });

  it("names an award by its case number", () => {
    const node = buildArbitralAwardNode(SITE, "/arbitral-award/A-1", {
      caseNumber: "ICC 1234",
      year: 2011,
      seatTown: "Geneva",
    });
    expect(node.name).toBe("Arbitral award ICC 1234");
    expect(node.datePublished).toBe("2011");
  });
});

describe("buildOrganization and buildDataset", () => {
  it("gives the organisation a stable id the other nodes reference", () => {
    expect(buildOrganization(SITE)["@id"]).toBe(
      "https://cold.global/#organization",
    );
  });

  it("marks the dataset as free and CC BY licensed", () => {
    const node = buildDataset(SITE);
    expect(node["@type"]).toBe("Dataset");
    expect(node.isAccessibleForFree).toBe(true);
    expect(node.license).toBe("https://creativecommons.org/licenses/by/4.0/");
  });
});

describe("buildFaqPage and buildDefinedTermSet", () => {
  it("keeps only entries with both halves", () => {
    const node = buildFaqPage([
      { question: "What is CoLD?", answer: "<p>A database.</p>" },
      { question: "Incomplete", answer: "" },
    ]);
    expect(node?.mainEntity).toEqual([
      {
        "@type": "Question",
        name: "What is CoLD?",
        acceptedAnswer: { "@type": "Answer", text: "A database." },
      },
    ]);
  });

  it("returns null when there is nothing to describe", () => {
    expect(buildFaqPage([])).toBeNull();
    expect(buildDefinedTermSet(SITE, "/learn/glossary", [])).toBeNull();
  });

  it("links every term back to the set", () => {
    const node = buildDefinedTermSet(SITE, "/learn/glossary", [
      { term: "Renvoi", definition: "Referral to another legal system." },
    ]);
    const terms = node?.hasDefinedTerm as { inDefinedTermSet: unknown }[];
    expect(terms[0]?.inDefinedTermSet).toEqual({
      "@id": "https://cold.global/learn/glossary#glossary",
    });
  });
});
