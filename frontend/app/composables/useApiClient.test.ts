import { describe, it, expect, vi, beforeEach } from "vitest";

global.fetch = vi.fn();

const { useApiClient } = await import("./useApiClient");

describe("useApiClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns a client with typed HTTP methods", () => {
    const { client } = useApiClient();
    expect(client).toBeDefined();
    expect(client.GET).toBeTypeOf("function");
    expect(client.POST).toBeTypeOf("function");
    expect(client.DELETE).toBeTypeOf("function");
  });

  it("makes requests through /api/proxy", async () => {
    const mockBody = {
      totalMatches: 0,
      results: [],
      test: false,
      page: 1,
      pageSize: 10,
    };
    global.fetch = vi.fn().mockResolvedValueOnce(
      new Response(JSON.stringify(mockBody), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );

    const { client } = useApiClient();
    await client.GET("/search/", {
      params: {
        query: {
          search_string: "test",
          page: 1,
          page_size: 10,
          sort_by_date: false,
        },
      },
    });

    expect(fetch).toHaveBeenCalledOnce();
    const request = vi.mocked(fetch).mock.calls[0]![0] as Request;
    expect(request.url).toContain("/api/proxy/search/");
    expect(request.method).toBe("GET");
  });
});
