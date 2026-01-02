import { createConfigForNuxt } from "@nuxt/eslint-config/flat";
import perfectionist from "eslint-plugin-perfectionist";

export default createConfigForNuxt({
  plugins: {
    perfectionist,
  },

  rules: {
    "perfectionist/sort-imports": [
      "error",
      {
        type: "alphabetical",
        order: "asc",
        ignoreCase: true,
        newlinesBetween: "always",
        maxLineLength: undefined,
        groups: [
          "type",
          ["builtin", "external"],
          "internal-type",
          "internal",
          ["parent-type", "sibling-type", "index-type"],
          ["parent", "sibling", "index"],
          "object",
          "unknown",
        ],
      },
    ],
    "perfectionist/sort-named-imports": [
      "error",
      {
        type: "alphabetical",
        order: "asc",
        ignoreCase: true,
      },
    ],
    "perfectionist/sort-objects": [
      "error",
      {
        type: "alphabetical",
        order: "asc",
        ignoreCase: true,
        partitionByComment: false,
      },
    ],
  },
}).override("nuxt/vue/rules", {
  rules: {
    "vue/html-self-closing": "off",
  },
});
