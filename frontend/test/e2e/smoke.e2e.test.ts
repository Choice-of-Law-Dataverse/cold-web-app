import { describe, expect, it } from "vitest";
import { $fetch, setup } from "@nuxt/test-utils/e2e";

const host = process.env.NUXT_E2E_HOST ?? "http://localhost:3000";

await setup({
  host,
  build: false,
  server: false,
});

const publicPages = [
  { path: "/", marker: "Choice of Law Dataverse" },
  { path: "/search", marker: "Search — CoLD" },
  { path: "/arbitral-award", marker: "Arbitral Awards" },
  { path: "/arbitral-institution", marker: "Arbitral Institutions" },
  { path: "/arbitral-rule", marker: "Arbitral Rules" },
  { path: "/court-decision", marker: "Court Decisions" },
  { path: "/domestic-instrument", marker: "Domestic Instruments" },
  { path: "/international-instrument", marker: "International Instruments" },
  { path: "/literature", marker: "Literature" },
  { path: "/regional-instrument", marker: "Regional Instruments" },
  { path: "/specialist", marker: "Specialists" },
  { path: "/disclaimer", marker: "Disclaimer — CoLD" },
  { path: "/contact", marker: "Contact — CoLD" },
  { path: "/learn/faq", marker: "FAQ — CoLD" },
  { path: "/learn/methodology", marker: "Methodology — CoLD" },
  { path: "/learn/glossary", marker: "Glossary — CoLD" },
  { path: "/learn/data-sets", marker: "Data Sets — CoLD" },
  { path: "/about/team", marker: "Team — CoLD" },
  { path: "/about/supporters", marker: "Supporters — CoLD" },
  { path: "/about/press", marker: "Press — CoLD" },
];

describe("public pages render server-side", () => {
  it.each(publicPages)(
    "$path responds with 200 and expected content",
    async ({ path, marker }) => {
      const html = await $fetch<string>(path);

      expect(typeof html).toBe("string");
      expect(html).toContain(marker);
    },
  );
});

describe("backend integration through the proxy", () => {
  it("statistics/counts returns real record counts", async () => {
    const body = await $fetch<{ counts: Record<string, number> }>(
      "/api/proxy/statistics/counts",
    );

    expect(body.counts).toBeTypeOf("object");
    expect(body.counts.courtDecisions).toBeGreaterThan(0);
    expect(body.counts.literature).toBeGreaterThan(0);
  });

  it("search/full_table returns rows for a populated table", async () => {
    const rows = await $fetch<unknown[]>("/api/proxy/search/full_table", {
      query: { table: "Court Decisions" },
    });

    expect(Array.isArray(rows)).toBe(true);
    expect(rows.length).toBeGreaterThan(0);
  });
});
