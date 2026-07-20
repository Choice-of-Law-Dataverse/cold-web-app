import { describe, expect, it } from "vitest";
import { createPage, setup, url } from "@nuxt/test-utils/e2e";

const host = process.env.NUXT_E2E_HOST ?? "http://localhost:3000";

await setup({
  host,
  build: false,
  server: false,
  browser: true,
  browserOptions: { type: "chromium" },
});

describe("header navigation", () => {
  it("navigates between routes via nav links without a full reload", async () => {
    const page = await createPage();
    try {
      await page.goto(url("/"), { waitUntil: "hydration" });

      await page
        .getByRole("link", { name: "Contact", exact: true })
        .first()
        .click();
      await page.waitForURL("**/contact");
      expect(new URL(page.url()).pathname).toBe("/contact");

      await page.getByRole("link", { name: "Home" }).first().click();
      await page.waitForURL((url) => url.pathname === "/");
      expect(new URL(page.url()).pathname).toBe("/");
    } finally {
      await page.close();
    }
  });

  it("opens the mobile menu and navigates from it", async () => {
    const page = await createPage(undefined, {
      viewport: { width: 500, height: 900 },
    });
    try {
      await page.goto(url("/"), { waitUntil: "hydration" });

      await page.getByRole("button", { name: "Menu" }).first().click();
      const menu = page.locator("#mobile-nav-menu");
      await menu.waitFor({ state: "visible", timeout: 10000 });

      await menu.getByRole("link", { name: "Contact", exact: true }).click();
      await page.waitForURL("**/contact");
      expect(new URL(page.url()).pathname).toBe("/contact");
    } finally {
      await page.close();
    }
  });
});

describe("entity list", () => {
  it("loads live rows from the backend", async () => {
    const page = await createPage();
    try {
      await page.goto(url("/court-decision"), { waitUntil: "hydration" });
      await page.waitForSelector('[data-testid="entity-row-link"]', {
        timeout: 20000,
      });

      const rowCount = await page
        .locator('[data-testid="entity-row-link"]')
        .count();
      expect(rowCount).toBeGreaterThan(0);
    } finally {
      await page.close();
    }
  });
});

describe("entity drawer", () => {
  it("opens on row click and closes via the close button", async () => {
    const page = await createPage();
    try {
      await page.goto(url("/court-decision"), { waitUntil: "hydration" });
      await page.waitForSelector('[data-testid="entity-row-link"]', {
        timeout: 20000,
      });

      const pathBeforeClick = new URL(page.url()).pathname;
      await page.locator('[data-testid="entity-row-link"]').first().click();

      const drawer = page.locator('[data-testid="entity-drawer"]');
      await drawer.waitFor({ state: "visible", timeout: 15000 });
      expect(new URL(page.url()).pathname).toBe(pathBeforeClick);

      await page.getByRole("button", { name: "Close" }).first().click();
      await drawer.waitFor({ state: "hidden", timeout: 15000 });
    } finally {
      await page.close();
    }
  });

  it("navigates to the full detail page via the Full page button", async () => {
    const page = await createPage();
    try {
      await page.goto(url("/court-decision"), { waitUntil: "hydration" });
      await page.waitForSelector('[data-testid="entity-row-link"]', {
        timeout: 20000,
      });

      await page.locator('[data-testid="entity-row-link"]').first().click();
      await page
        .locator('[data-testid="entity-drawer"]')
        .waitFor({ state: "visible", timeout: 15000 });

      await page
        .getByRole("link", { name: /Full page/i })
        .first()
        .click();
      await page.waitForURL("**/court-decision/**", { timeout: 15000 });
      expect(new URL(page.url()).pathname).toMatch(/^\/court-decision\/.+/);
    } finally {
      await page.close();
    }
  });
});

describe("search", () => {
  it("runs a query from the nav bar and shows results", async () => {
    const page = await createPage();
    try {
      await page.goto(url("/"), { waitUntil: "hydration" });

      const input = page.getByPlaceholder("Search").first();
      await input.click();
      await input.fill("party autonomy");
      await input.press("Enter");

      await page.waitForURL("**/search**", { timeout: 15000 });
      expect(new URL(page.url()).pathname).toBe("/search");
      expect(new URL(page.url()).searchParams.get("q")).toBe("party autonomy");

      const resultLink = page.locator('main a[href*="/court-decision/"]');
      await resultLink.first().waitFor({ state: "visible", timeout: 20000 });
      expect(await resultLink.count()).toBeGreaterThan(0);
    } finally {
      await page.close();
    }
  });
});

describe("jurisdiction comparison", () => {
  it("compares Germany with France via the add-comparison select", async () => {
    const page = await createPage();
    try {
      await page.goto(url("/jurisdiction/DEU"), { waitUntil: "hydration" });

      const select = page.locator(
        '[data-testid="jurisdiction-compare-select"]',
      );
      await select.waitFor({ state: "visible", timeout: 20000 });
      await select.click();

      const search = page.getByPlaceholder("Search a Jurisdiction...");
      await search.waitFor({ state: "visible", timeout: 10000 });
      await search.fill("France");
      await page
        .getByRole("option", { name: /France/i })
        .first()
        .click();

      const grid = page.locator('[data-testid="comparison-grid"]');
      await grid.waitFor({ state: "visible", timeout: 30000 });
      await page
        .locator(".comparison-match-stats__value")
        .first()
        .waitFor({ state: "visible", timeout: 30000 });

      const gridText = await grid.innerText();
      expect(gridText).toContain("Germany");
      expect(gridText).toContain("France");
    } finally {
      await page.close();
    }
  });
});
