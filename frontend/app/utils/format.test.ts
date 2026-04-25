import { describe, it, expect } from "vitest";
import { parseSortableDate } from "./format";

describe("parseSortableDate", () => {
  it("parses DD.MM.YYYY into a sortable timestamp", () => {
    expect(parseSortableDate("20.02.1951")).toBe(Date.UTC(1951, 1, 20));
  });

  it("parses ISO dates", () => {
    expect(parseSortableDate("2024-05-12")).toBe(Date.UTC(2024, 4, 12));
  });

  it("returns null for missing or unparseable input", () => {
    expect(parseSortableDate(undefined)).toBeNull();
    expect(parseSortableDate(null)).toBeNull();
    expect(parseSortableDate("")).toBeNull();
    expect(parseSortableDate("   ")).toBeNull();
    expect(parseSortableDate("not a date")).toBeNull();
  });

  it("orders newest first when used as a sort key (descending)", () => {
    const items = [
      "20.02.1951",
      "13.03.1985",
      "23.03.1965",
      "2024-01-15",
      "",
      "garbage",
    ];
    const sorted = [...items].sort((a, b) => {
      const aKey = parseSortableDate(a);
      const bKey = parseSortableDate(b);
      if (aKey !== null && bKey !== null) return bKey - aKey;
      if (aKey !== null) return -1;
      if (bKey !== null) return 1;
      return 0;
    });
    expect(sorted.slice(0, 4)).toEqual([
      "2024-01-15",
      "13.03.1985",
      "23.03.1965",
      "20.02.1951",
    ]);
  });
});
