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
      GET: vi.fn().mockResolvedValue({ data: [], error: null }),
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
        queryKey: ["Questions", undefined, null, null, null],
      }),
    );
  });

  it("includes filters in query key when provided", () => {
    const filters = [{ column: "question" as const, value: "Test" }];

    useFullTable("Questions", { filters });

    expect(useQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["Questions", JSON.stringify(filters), null, null, null],
      }),
    );
  });

  it("disambiguates filter sets that previously collided on join", () => {
    const singleCsvValue = [{ column: "question" as const, value: "a,b" }];
    const twoSeparateValues = [
      { column: "question" as const, value: "a" },
      { column: "question" as const, value: "b" },
    ];

    useFullTable("Questions", { filters: singleCsvValue });
    const [firstArg] = vi.mocked(useQuery).mock.calls.at(-1)!;
    const firstKey = (firstArg as { queryKey: unknown }).queryKey;

    useFullTable("Questions", { filters: twoSeparateValues });
    const [secondArg] = vi.mocked(useQuery).mock.calls.at(-1)!;
    const secondKey = (secondArg as { queryKey: unknown }).queryKey;

    expect(firstKey).not.toEqual(secondKey);
  });

  it("includes pagination params in query key when provided", () => {
    useFullTable("Questions", {
      limit: 5,
      orderBy: "date",
      orderDir: "desc",
    });

    expect(useQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["Questions", undefined, 5, "date", "desc"],
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
