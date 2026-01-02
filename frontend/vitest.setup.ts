import { vi } from "vitest";

// Mock Nuxt runtime config
vi.stubGlobal("useRuntimeConfig", () => ({
  public: {
    siteUrl: "https://test.example.com",
  },
}));

// Mock global fetch if not available
if (!global.fetch) {
  global.fetch = vi.fn();
}
