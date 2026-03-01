import { describe, it, expect } from "vitest";
import { ref } from "vue";
import { useCardFields } from "./useCardFields";

const makeConfig = (overrides = {}) => ({
  keyLabelPairs: [
    {
      key: "Title",
      label: "Case Title",
      emptyValueBehavior: {
        action: "display" as const,
        fallback: "No title available",
      },
    },
    {
      key: "Date",
      label: "Date",
      emptyValueBehavior: { action: "hide" as const },
    },
    { key: "Author", label: "Author(s)" },
  ],
  valueClassMap: {
    Title: "result-value-medium",
    Date: "result-value-small",
    Author: "result-value-small",
  },
  ...overrides,
});

describe("useCardFields", () => {
  describe("getLabel", () => {
    it("returns the configured label for a known key", () => {
      const { getLabel } = useCardFields(makeConfig(), { Title: "Test" });
      expect(getLabel("Title")).toBe("Case Title");
    });

    it("returns the key itself when no label is configured", () => {
      const { getLabel } = useCardFields(makeConfig(), { Title: "Test" });
      expect(getLabel("Unknown")).toBe("Unknown");
    });
  });

  describe("getValue", () => {
    it("returns the value when present", () => {
      const { getValue } = useCardFields(makeConfig(), { Title: "My Case" });
      expect(getValue("Title")).toBe("My Case");
    });

    it("returns fallback when value is empty and action is display", () => {
      const { getValue } = useCardFields(makeConfig(), { Title: "" });
      expect(getValue("Title")).toBe("No title available");
    });

    it("returns fallback when value is NA and action is display", () => {
      const { getValue } = useCardFields(makeConfig(), { Title: "NA" });
      expect(getValue("Title")).toBe("No title available");
    });

    it("returns empty string when value is empty and action is hide", () => {
      const { getValue } = useCardFields(makeConfig(), { Date: "" });
      expect(getValue("Date")).toBe("");
    });

    it("supports getFallback callback", () => {
      const config = makeConfig({
        keyLabelPairs: [
          {
            key: "Title",
            label: "Title",
            emptyValueBehavior: {
              action: "display",
              getFallback: (data: Record<string, unknown>) =>
                (data["Citation"] as string) || "fallback",
            },
          },
        ],
      });
      const { getValue } = useCardFields(config, {
        Title: "",
        Citation: "Case 123",
      });
      expect(getValue("Title")).toBe("Case 123");
    });

    it("works with ref-wrapped data", () => {
      const data = ref({ Title: "Ref Title" });
      const { getValue } = useCardFields(makeConfig(), data);
      expect(getValue("Title")).toBe("Ref Title");
    });
  });

  describe("shouldDisplay", () => {
    it("returns true when action is display regardless of value", () => {
      const { shouldDisplay } = useCardFields(makeConfig(), { Title: "" });
      expect(shouldDisplay("Title")).toBe(true);
    });

    it("returns false when action is hide and value is empty", () => {
      const { shouldDisplay } = useCardFields(makeConfig(), { Date: "" });
      expect(shouldDisplay("Date")).toBe(false);
    });

    it("returns true when action is hide but value exists", () => {
      const { shouldDisplay } = useCardFields(makeConfig(), {
        Date: "2024-01-01",
      });
      expect(shouldDisplay("Date")).toBe(true);
    });

    it("respects shouldDisplay callback from config", () => {
      const config = makeConfig({
        keyLabelPairs: [
          {
            key: "Publisher",
            label: "Publisher",
            emptyValueBehavior: {
              action: "display",
              fallback: "N/A",
              shouldDisplay: (data: Record<string, unknown>) =>
                data["Type"] === "book",
            },
          },
        ],
      });
      const { shouldDisplay } = useCardFields(config, {
        Publisher: "Springer",
        Type: "article",
      });
      expect(shouldDisplay("Publisher")).toBe(false);
    });
  });

  describe("computeTextClasses", () => {
    it("includes base class and text classes", () => {
      const { computeTextClasses } = useCardFields(makeConfig(), {
        Title: "Present",
      });
      const classes = computeTextClasses("Title", "result-value-medium");
      expect(classes).toContain("result-value-medium");
      expect(classes).toContain("text-sm leading-relaxed whitespace-pre-line");
    });

    it("adds text-gray-400 for empty display fields", () => {
      const { computeTextClasses } = useCardFields(makeConfig(), {
        Title: "",
      });
      const classes = computeTextClasses("Title", "result-value-medium");
      expect(classes).toContain("text-gray-400");
    });

    it("does not add text-gray-400 for non-empty fields", () => {
      const { computeTextClasses } = useCardFields(makeConfig(), {
        Title: "Has Value",
      });
      const classes = computeTextClasses("Title", "result-value-medium");
      expect(classes).not.toContain("text-gray-400");
    });
  });

  describe("fieldClasses", () => {
    it("combines valueClassMap with text classes", () => {
      const { fieldClasses } = useCardFields(makeConfig(), {
        Title: "Present",
      });
      const classes = fieldClasses("Title");
      expect(classes).toContain("result-value-medium");
      expect(classes).toContain("text-sm leading-relaxed whitespace-pre-line");
    });

    it("uses empty string when key not in valueClassMap", () => {
      const { fieldClasses } = useCardFields(makeConfig(), {
        Unknown: "value",
      });
      const classes = fieldClasses("Unknown");
      expect(classes[0]).toBe("");
    });
  });

  describe("processedData", () => {
    it("applies processData when configured", () => {
      const config = makeConfig({
        processData: (data: Record<string, unknown>) => ({
          ...data,
          Title: `Processed: ${data["Title"]}`,
        }),
      });
      const { getValue } = useCardFields(config, { Title: "Raw" });
      expect(getValue("Title")).toBe("Processed: Raw");
    });

    it("returns raw data when processData is not configured", () => {
      const { getValue } = useCardFields(makeConfig(), { Title: "Raw" });
      expect(getValue("Title")).toBe("Raw");
    });
  });
});
