import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("@tanstack/vue-query", () => ({
  useQuery: vi.fn((options) => ({
    data: { value: [] },
    isLoading: false,
    error: null,
    queryKey: options.queryKey,
    queryFn: options.queryFn,
  })),
}));

vi.mock("./useApiClient", () => ({
  useApiClient: vi.fn(() => ({
    client: {
      POST: vi.fn().mockResolvedValue({ data: [], error: null }),
    },
  })),
}));

const { useQuery } = await import("@tanstack/vue-query");
const { useFullTable } = await import("./useFullTable");

describe("useFullTable", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls useQuery with correct table name", () => {
    useFullTable("Questions");

    expect(useQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["Questions", undefined],
      }),
    );
  });

  it("includes filters in query key when provided", () => {
    const filters = [{ column: "question" as const, value: "Test" }];

    useFullTable("Questions", { filters });

    expect(useQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["Questions", "Test"],
      }),
    );
  });

  it("returns query result", () => {
    const result = useFullTable("Jurisdictions");

    expect(result).toHaveProperty("data");
    expect(result).toHaveProperty("isLoading");
    expect(result).toHaveProperty("error");
  });

  it("passes select function to useQuery when provided", () => {
    const selectFn = (data: unknown[]) => data;

    useFullTable("Questions", { select: selectFn });

    expect(useQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        select: selectFn,
      }),
    );
  });
});
