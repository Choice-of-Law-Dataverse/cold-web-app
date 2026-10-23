import { describe, it, expect, vi, beforeEach } from "vitest";
import type { SSEEvent, SSEStreamOptions } from "~/utils/sseStream";

type ScriptItem = SSEEvent | (() => void) | Error;

let script: ScriptItem[] = [];

vi.mock("~/utils/sseStream", () => ({
  streamSSE: vi.fn(async (options: SSEStreamOptions<unknown>) => {
    for (const item of script) {
      if (item instanceof Error) throw item;
      if (typeof item === "function") item();
      else options.onEvent?.(item);
    }
    return { completedSteps: new Set(), lastEvent: null };
  }),
}));

vi.stubGlobal("useToast", () => ({ add: vi.fn() }));

const { useCaseAnalysisSession } = await import("./useCaseAnalysisSession");

const completed = (step: string, data: Record<string, unknown>): SSEEvent => ({
  step,
  status: "completed",
  data,
});

function startedSession() {
  const session = useCaseAnalysisSession();
  session.draftId.value = 7;
  return session;
}

describe("useCaseAnalysisSession", () => {
  beforeEach(() => {
    script = [];
  });

  it("fills the form as steps complete", async () => {
    const session = startedSession();
    script = [
      completed("case_citation", { case_citation: "Smith v Jones" }),
      completed("theme_classification", {
        themes: ["Party autonomy", "Tacit"],
      }),
    ];

    await session.analyze();

    expect(session.stage.value).toBe("analyzing");
    expect(session.editableForm.caseCitation).toBe("Smith v Jones");
    expect(session.editableForm.themes).toBe("Party autonomy, Tacit");
    expect(session.getFieldStatus("caseCitation")?.status).toBe("completed");
  });

  it("keeps a user's edit while later steps stream in", async () => {
    const session = startedSession();
    script = [
      completed("case_citation", { case_citation: "Smith v Jones" }),
      () => {
        session.editableForm.caseCitation = "Smith v. Jones [2024] UKSC 1";
      },
      completed("relevant_facts", { relevant_facts: "A contract." }),
      completed("abstract", { abstract: "Summary." }),
    ];

    await session.analyze();

    expect(session.editableForm.caseCitation).toBe(
      "Smith v. Jones [2024] UKSC 1",
    );
    expect(session.editableForm.caseRelevantFacts).toBe("A contract.");
    expect(session.editableForm.caseAbstract).toBe("Summary.");
  });

  it("keeps a field the user cleared", async () => {
    const session = startedSession();
    script = [
      completed("case_citation", { case_citation: "Smith v Jones" }),
      () => {
        session.editableForm.caseCitation = "";
      },
      completed("abstract", { abstract: "Summary." }),
    ];

    await session.analyze();

    expect(session.editableForm.caseCitation).toBe("");
  });

  it("forgets edits when re-analysing with a chosen jurisdiction", async () => {
    const session = startedSession();
    script = [completed("case_citation", { case_citation: "First" })];
    await session.analyze();
    session.editableForm.caseCitation = "Edited";

    script = [completed("case_citation", { case_citation: "Second" })];
    await session.reAnalyze("Common-law", {
      name: "England",
      label: "England",
      coldId: "GBR",
    });

    expect(session.editableForm.caseCitation).toBe("Second");
    expect(session.editableForm.jurisdiction).toBe("England");
    expect(session.isCommonLawJurisdiction.value).toBe(true);
  });

  it("reports a failed analysis and marks running steps as failed", async () => {
    const session = startedSession();
    script = [
      { step: "col_issue", status: "in_progress" },
      new Error("Stream dropped"),
    ];

    await session.analyze();

    expect(session.error.value).toBe("Stream dropped");
    expect(session.getFieldStatus("caseChoiceofLawIssue")?.status).toBe(
      "error",
    );
    expect(session.isAnalyzing.value).toBe(false);
  });

  it("does nothing without a draft", async () => {
    const session = useCaseAnalysisSession();

    await session.analyze();

    expect(session.stage.value).toBe("upload");
  });

  it("returns every part of the run to the upload stage on reset", async () => {
    const session = startedSession();
    script = [completed("case_citation", { case_citation: "Smith v Jones" })];
    await session.analyze();
    session.error.value = "old";

    session.reset();

    expect(session.stage.value).toBe("upload");
    expect(session.error.value).toBeNull();
    expect(session.draftId.value).toBeNull();
    expect(session.editableForm.caseCitation).toBe("");
    expect(
      session.analysisSteps.value.every((step) => step.status === "pending"),
    ).toBe(true);
  });
});
