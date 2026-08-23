import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import openApiDocument from "../app/types/openapi.json";

const documentation = readFileSync(
  resolve(process.cwd(), "content/technical_documentation.md"),
  "utf8",
);

describe("technical documentation OpenAPI contract", () => {
  it("documents every core read endpoint using its production path", () => {
    const coreReadPaths = [
      "/search/",
      "/search/details",
      "/search/full_table",
      "/search/specialists/{jurisdiction_alpha_code}",
      "/entities/{slug}",
      "/statistics/counts",
      "/statistics/count-by-jurisdiction",
      "/statistics/jurisdictions-with-answer-percentage",
    ] as const;

    for (const path of coreReadPaths) {
      expect(openApiDocument.paths[path].get).toBeDefined();
      expect(documentation).toContain(`GET /api/v1${path}`);
    }
  });

  it("keeps the public dataset table aligned with the bulk endpoint", () => {
    const bulkDescription =
      openApiDocument.paths["/search/full_table"].get.description;
    const availableTables = /\*\*Available tables:\*\* ([^.]+)\./.exec(
      bulkDescription,
    )?.[1];
    const documentedDatasets = documentation
      .split("\n")
      .filter((line) => line.startsWith("|"))
      .map((line) => line.split("|")[1]?.trim());

    expect(availableTables).toBeTruthy();

    for (const table of availableTables?.split(", ") ?? []) {
      expect(documentedDatasets).toContain(table);
    }
  });

  it("publishes the OpenAPI pagination limits and stable search anchor", () => {
    const searchPageSize = openApiDocument.paths[
      "/search/"
    ].get.parameters.find(({ name }) => name === "page_size");
    const entityPageSize = openApiDocument.paths[
      "/entities/{slug}"
    ].get.parameters.find(({ name }) => name === "page_size");

    expect(searchPageSize?.schema.maximum).toBe(100);
    expect(entityPageSize?.schema.maximum).toBe(250);
    expect(documentation).toContain("at most 100 results per page");
    expect(documentation).toContain("at most 250 records per page");
    expect(documentation).toContain("## Search");
  });
});
