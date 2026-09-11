import { globSync, readFileSync } from "node:fs";
import { basename, resolve } from "node:path";
import { describe, expect, it } from "vitest";

const QUERY_PATH =
  /queryCollection\(\s*["']content["']\s*\)[\s\S]*?\.path\(\s*["']([^"']+)["']\s*\)/g;

const markdownPaths = globSync("content/**/*.md", { cwd: process.cwd() }).map(
  (file) => `/${basename(file, ".md")}`,
);

const queriedPaths = globSync("app/**/*.vue", { cwd: process.cwd() }).flatMap(
  (file) => {
    const source = readFileSync(resolve(process.cwd(), file), "utf8");
    return [...source.matchAll(QUERY_PATH)].map((match) => ({
      file,
      path: match[1] as string,
    }));
  },
);

describe("content collection queries", () => {
  it("finds at least one queried content path", () => {
    expect(queriedPaths.length).toBeGreaterThan(0);
  });

  it.each(queriedPaths)(
    "$file queries $path, which has a markdown document",
    ({ path }) => {
      expect(markdownPaths).toContain(path);
    },
  );
});
