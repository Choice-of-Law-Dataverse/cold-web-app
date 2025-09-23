import { createConfigForNuxt } from "@nuxt/eslint-config/flat";
import perfectionist from "eslint-plugin-perfectionist";

export default createConfigForNuxt(
  // Your custom configs here
  {
    plugins: {
      perfectionist,
    },
    rules: {
      // Perfectionist rules for sorting and organizing code
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
  },
);
