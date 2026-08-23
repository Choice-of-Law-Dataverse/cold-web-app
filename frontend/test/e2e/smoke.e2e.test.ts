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
  {
    path: "/learn/technical-documentation",
    marker: "Technical Documentation — CoLD",
  },
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

  it("publishes the migrated search documentation at a stable anchor", async () => {
    const html = await $fetch<string>("/learn/technical-documentation");

    expect(html).toContain('id="search"');
    expect(html).toContain("PostgreSQL full-text search");
  });
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

describe("entity pages render their content server-side", () => {
  const entityPages = [
    {
      path: "/court-decision/CD-ISR-524",
      marker: "Klausner v Berkovitz",
      label: "Court Decision",
    },
    {
      path: "/jurisdiction/CHE",
      marker: "Choice of law in Switzerland",
      label: "Jurisdiction",
    },
  ];

  it.each(entityPages)(
    "$path puts the record title in the SSR title and an h1",
    async ({ path, marker, label }) => {
      const html = await $fetch<string>(path);

      expect(html).toContain(`<title>${marker}`);
      expect(html).toMatch(new RegExp(`<h1[^>]*>${marker}</h1>`));
      expect(html).not.toContain(`<title>${label} — CoLD</title>`);
    },
  );

  it("gives each record a description that is not just its title", async () => {
    const html = await $fetch<string>("/court-decision/CD-ISR-524");
    const description = /<meta name="description" content="([^"]*)"/.exec(
      html,
    )?.[1];

    expect(description).toBeTruthy();
    expect(description).not.toBe("Court Decision — CoLD");
  });

  it("emits structured data for a record", async () => {
    const html = await $fetch<string>("/court-decision/CD-ISR-524");

    expect(html).toContain("application/ld+json");
    expect(html).toContain('"BreadcrumbList"');
  });
});

describe("every indexable page has exactly one h1", () => {
  const headingPages = [
    "/",
    "/court-decision",
    "/court-decision/CD-ISR-524",
    "/jurisdiction/CHE",
    "/literature",
    "/specialist",
    "/learn/faq",
    "/learn/glossary",
    "/learn/methodology",
    "/learn/data-sets",
    "/learn/technical-documentation",
    "/about/team",
    "/about/about-cold",
    "/contact",
    "/disclaimer",
  ];

  it.each(headingPages)("%s", async (path) => {
    const html = await $fetch<string>(path);
    const headings = (html.match(/<h1[\s>]/g) ?? []).length;

    expect(headings).toBe(1);
  });
});

describe("canonical URLs collapse duplicates", () => {
  it.each([
    "/court-decision/",
    "/court-decision?page=3&foo=bar",
    "/court-decision",
  ])("%s canonicalises to the bare path", async (path) => {
    const html = await $fetch<string>(path);
    const canonical = /<link rel="canonical" href="([^"]*)"/.exec(html)?.[1];

    expect(canonical).toBeTruthy();
    expect(canonical?.endsWith("/court-decision")).toBe(true);
  });
});

describe("missing records are not soft 404s", () => {
  it.each(["/court-decision/CD-DOES-NOT-EXIST", "/literature/DOES-NOT-EXIST"])(
    "%s responds 404",
    async (path) => {
      const response = await fetch(new URL(path, host), {
        headers: { accept: "text/html" },
      });

      expect(response.status).toBe(404);
    },
  );
});

describe("thin question answers stay out of the index", () => {
  it("marks a jurisdiction-specific answer noindex", async () => {
    const html = await $fetch<string>("/question/CPV_28-Arb");

    expect(html).toMatch(/<meta name="robots"[^>]*content="noindex, follow"/);
  });
});

describe("cache policy", () => {
  async function cacheControl(path: string) {
    const response = await fetch(new URL(path, host), {
      headers: { accept: "text/html" },
    });
    return response.headers.get("cache-control") ?? "";
  }

  it.each([
    "/",
    "/court-decision",
    "/court-decision/CD-ISR-524",
    "/jurisdiction/CHE",
    "/question/01-P",
    "/learn/faq",
  ])(
    "%s is shared-cacheable but always revalidated by the browser",
    async (path) => {
      const header = await cacheControl(path);

      expect(header).toContain("s-maxage=");
      expect(header).toContain("max-age=0");
      expect(header).not.toContain("no-store");
    },
  );

  it.each([
    "/search",
    "/moderation",
    "/court-decision/new",
    "/court-decision/my-analyses",
    "/literature/new",
    "/international-instrument/II-HCCH-1/edit",
  ])("%s is never stored by a shared cache", async (path) => {
    const header = await cacheControl(path);

    expect(header).toContain("no-store");
    expect(header).not.toContain("s-maxage");
  });
});

describe("server-rendered HTML does not vary by session", () => {
  it("keeps the signed-in entity action off the server render", async () => {
    const html = await $fetch<string>("/court-decision/CD-ISR-524");

    expect(html).not.toContain('href="/court-decision/new"');
  });
});

describe("sitemap", () => {
  it("indexes one sitemap per entity collection", async () => {
    const xml = await $fetch<string>("/sitemap_index.xml");

    for (const name of [
      "pages",
      "court-decisions",
      "jurisdictions",
      "literature",
      "domestic-instruments",
      "specialists",
      "questions",
    ]) {
      expect(xml).toContain(`/__sitemap__/${name}.xml`);
    }
  });

  it("lists real detail URLs, not just static routes", async () => {
    const xml = await $fetch<string>("/__sitemap__/court-decisions.xml");
    const locations = xml.match(/<loc>/g) ?? [];

    expect(locations.length).toBeGreaterThan(1000);
    expect(xml).toContain("/court-decision/CD-");
  });

  it("omits the jurisdiction-specific question answers", async () => {
    const xml = await $fetch<string>("/__sitemap__/questions.xml");
    const answerUrls = xml.match(
      /<loc>[^<]*\/question\/[A-Z]{3}_[^<]*<\/loc>/g,
    );

    expect(answerUrls).toBeNull();
  });

  it("keeps gated routes out of the pages sitemap", async () => {
    const xml = await $fetch<string>("/__sitemap__/pages.xml");

    for (const path of ["/search", "/moderation", "/new", "/edit"]) {
      expect(xml).not.toContain(`${path}</loc>`);
    }
  });
});
