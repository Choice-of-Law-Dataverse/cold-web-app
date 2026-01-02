import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock global fetch
global.fetch = vi.fn();

// Import after mocks are set up
const { useApiClient } = await import("./useApiClient");

describe("useApiClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns an apiClient function", () => {
    const client = useApiClient();
    expect(client.apiClient).toBeTypeOf("function");
  });

  it("calls fetch with correct default parameters", async () => {
    const mockResponse = { data: "test" };
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const client = useApiClient();
    await client.apiClient("/test-endpoint");

    expect(fetch).toHaveBeenCalledWith(
      "/api/proxy/test-endpoint",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "Content-Type": "application/json",
        }),
      }),
    );
  });

  it("sends body as JSON string when provided", async () => {
    const mockResponse = { data: "test" };
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const client = useApiClient();
    const body = { table: "Questions" } as const;
    await client.apiClient("/test-endpoint", { body });

    expect(fetch).toHaveBeenCalledWith(
      "/api/proxy/test-endpoint",
      expect.objectContaining({
        body: JSON.stringify(body),
      }),
    );
  });

  it("throws NotFoundError for 404 responses", async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: "Not Found",
    });

    const client = useApiClient();

    await expect(client.apiClient("/test-endpoint")).rejects.toThrow();
  });

  it("throws ApiError for non-404 error responses", async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
    });

    const client = useApiClient();

    await expect(client.apiClient("/test-endpoint")).rejects.toThrow();
  });

  it("returns parsed JSON response on success", async () => {
    const mockResponse = { data: "test", status: "success" };
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const client = useApiClient();
    const result = await client.apiClient("/test-endpoint");

    expect(result).toEqual(mockResponse);
  });
});
