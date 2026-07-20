import { configDefaults, defineConfig } from "vitest/config";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath } from "node:url";

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: "happy-dom",
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
    exclude: [...configDefaults.exclude, "test/e2e/**"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/",
        ".nuxt/",
        "dist/",
        "**/*.config.*",
        "**/*.d.ts",
        "**/types/**",
      ],
    },
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./app", import.meta.url)),
      "~": fileURLToPath(new URL("./app", import.meta.url)),
      "#components": fileURLToPath(
        new URL("./vitest-components-mock.ts", import.meta.url),
      ),
    },
  },
});
