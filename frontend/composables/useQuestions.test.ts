import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock useFullTable
vi.mock("./useFullTable", () => ({
  useFullTable: vi.fn((tableName) => ({
    data: { value: [] },
    isLoading: false,
    error: null,
    tableName,
  })),
}));

const { useFullTable } = await import("./useFullTable");
const { useQuestions } = await import("./useQuestions");

describe("useQuestions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls useFullTable with 'Questions' table name", () => {
    const result = useQuestions();

    expect(useFullTable).toHaveBeenCalledWith("Questions");
    expect(result.tableName).toBe("Questions");
  });

  it("returns query result from useFullTable", () => {
    const result = useQuestions();

    expect(result).toHaveProperty("data");
    expect(result).toHaveProperty("isLoading");
    expect(result).toHaveProperty("error");
  });
});
