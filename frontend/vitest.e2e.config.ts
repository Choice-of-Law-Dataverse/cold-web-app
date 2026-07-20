import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    include: ["test/e2e/**/*.e2e.test.ts"],
    testTimeout: 30000,
    hookTimeout: 60000,
  },
});
