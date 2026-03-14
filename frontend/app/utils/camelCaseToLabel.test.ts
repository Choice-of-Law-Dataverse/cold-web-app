import { describe, it, expect } from "vitest";
import { camelCaseToLabel } from "./camelCaseToLabel";

describe("camelCaseToLabel", () => {
  it("converts simple camelCase", () => {
    expect(camelCaseToLabel("caseTitle")).toBe("Case Title");
  });

  it("handles single word", () => {
    expect(camelCaseToLabel("title")).toBe("Title");
  });

  it("handles multiple capitals", () => {
    expect(camelCaseToLabel("publicationDateIso")).toBe("Publication Date Iso");
  });

  it("handles long keys", () => {
    expect(camelCaseToLabel("textOfTheRelevantLegalProvisions")).toBe(
      "Text Of The Relevant Legal Provisions",
    );
  });

  it("handles already capitalized single word", () => {
    expect(camelCaseToLabel("Abstract")).toBe("Abstract");
  });
});
