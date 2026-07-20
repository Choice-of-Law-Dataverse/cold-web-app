import { describe, expect, it } from "vitest";
import { $fetch, setup } from "@nuxt/test-utils/e2e";

const host = process.env.NUXT_E2E_HOST ?? "http://localhost:3000";

await setup({
  host,
  build: false,
  server: false,
});

const publicReadRoutes = [
  { path: "/", marker: "Choice of Law Dataverse" },
  { path: "/court-decision", marker: "Court Decisions" },
  { path: "/literature", marker: "Literature" },
  { path: "/arbitral-award", marker: "Arbitral Awards" },
  { path: "/disclaimer", marker: "Disclaimer — CoLD" },
];

describe("public read routes render server-side", () => {
  it.each(publicReadRoutes)(
    "$path responds with 200 and expected content",
    async ({ path, marker }) => {
      const html = await $fetch<string>(path);

      expect(typeof html).toBe("string");
      expect(html).toContain(marker);
    },
  );
});
