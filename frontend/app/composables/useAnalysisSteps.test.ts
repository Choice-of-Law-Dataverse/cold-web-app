import { describe, expect, it } from "vitest";
import { useAnalysisSteps } from "./useAnalysisSteps";

describe("useAnalysisSteps", () => {
  it("shows pending field loaders only while the real analysis is running", () => {
    const { isFieldLoading, updateStepStatus } = useAnalysisSteps();

    expect(isFieldLoading("caseCitation")).toBe(false);
    expect(isFieldLoading("caseCitation", true)).toBe(true);

    updateStepStatus("case_citation", "completed");
    expect(isFieldLoading("caseCitation", true)).toBe(false);
  });
});
