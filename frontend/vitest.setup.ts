import { vi } from "vitest";
import { config } from "@vue/test-utils";

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

// Suppress Vue warnings about unresolved components in tests
// These are Nuxt auto-imported components that vue-test-utils automatically stubs
config.global.config.warnHandler = () => {
  // Suppress all warnings during tests
};
