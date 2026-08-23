import { describe, it, expect } from "vitest";
import {
  buildPageTitle,
  buildSeoDescription,
  stripMarkup,
  toAbsoluteUrl,
  toCanonicalPath,
  truncate,
} from "./seo";

describe("stripMarkup", () => {
  it("removes tags and collapses whitespace", () => {
    expect(stripMarkup("<p>Hello\n\n  <b>world</b></p>")).toBe("Hello world");
  });

  it("decodes the entities the backend emits", () => {
    expect(stripMarkup("Smith &amp; Co &quot;Ltd&quot;")).toBe(
      'Smith & Co "Ltd"',
    );
  });

  it("returns an empty string for nullish input", () => {
    expect(stripMarkup(null)).toBe("");
    expect(stripMarkup(undefined)).toBe("");
  });
});

describe("buildPageTitle", () => {
  it("puts the most specific part first and always ends with the site name", () => {
    expect(buildPageTitle(["Klausner v Berkovitz"], "Court Decision")).toBe(
      "Klausner v Berkovitz — CoLD",
    );
  });

  it("keeps the entity label when the caller passes it as the last part", () => {
    expect(
      buildPageTitle(
        ["Klausner v Berkovitz", "CA 750/79", "Court Decision"],
        "Court Decision",
      ),
    ).toBe("Klausner v Berkovitz — CA 750/79 — Court Decision — CoLD");
  });

  it("falls back to the entity label when every part is blank", () => {
    expect(buildPageTitle([null, "", "  "], "Court Decision")).toBe(
      "Court Decision — CoLD",
    );
  });

  it("drops a part that another part already contains", () => {
    expect(
      buildPageTitle(
        [
          "Klausner v Berkovitz",
          "Klausner v Berkovitz, CA 750/79, 37(4) PD 449",
          "Court Decision",
        ],
        "Court Decision",
      ),
    ).toBe("Klausner v Berkovitz — Court Decision — CoLD");
  });

  it("drops parts that repeat regardless of case", () => {
    expect(buildPageTitle(["Literature", "literature"], "Literature")).toBe(
      "Literature — CoLD",
    );
  });
});

describe("truncate", () => {
  it("leaves short text untouched", () => {
    expect(truncate("short", 20)).toBe("short");
  });

  it("cuts on a word boundary and marks the elision", () => {
    const result = truncate("the quick brown fox jumps over", 20);
    expect(result.endsWith("…")).toBe(true);
    expect(result.length).toBeLessThanOrEqual(20);
    expect(result).not.toContain("jum…");
  });
});

describe("buildSeoDescription", () => {
  it("joins real content instead of echoing the title", () => {
    const result = buildSeoDescription(
      ["CA 750/79", "Court of Appeal", "Concerns party autonomy"],
      "Court Decision",
    );
    expect(result).toBe("CA 750/79. Court of Appeal. Concerns party autonomy");
  });

  it("uses the fallback sentence when the record has no usable fields", () => {
    expect(
      buildSeoDescription([null, undefined, ""], "A generic sentence"),
    ).toBe("A generic sentence");
  });

  it("stays within the requested length", () => {
    const long = "word ".repeat(200);
    expect(buildSeoDescription([long], "x", 160).length).toBeLessThanOrEqual(
      160,
    );
  });
});

describe("toCanonicalPath", () => {
  it.each([
    ["/", "/"],
    ["", "/"],
    ["/court-decision/", "/court-decision"],
    ["/court-decision", "/court-decision"],
    ["/court-decision?page=3", "/court-decision"],
    ["/court-decision/?page=3&foo=bar", "/court-decision"],
    ["/court-decision#section", "/court-decision"],
  ])("normalises %s to %s", (input, expected) => {
    expect(toCanonicalPath(input)).toBe(expected);
  });
});

describe("toAbsoluteUrl", () => {
  it("joins without doubling slashes", () => {
    expect(toAbsoluteUrl("https://cold.global/", "/literature")).toBe(
      "https://cold.global/literature",
    );
  });

  it("keeps the root path", () => {
    expect(toAbsoluteUrl("https://cold.global", "/")).toBe(
      "https://cold.global/",
    );
  });
});
