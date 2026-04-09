import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { buildAllowedOrigins, validateOrigin } from "./validateOrigin";

vi.mock("@pydantic/logfire-node", () => ({
  warning: vi.fn(),
}));

const mockGetHeader = vi.fn();
const mockCreateError = vi.fn(
  (opts: { statusCode: number; message: string }) => {
    const err = new Error(opts.message) as Error & { statusCode: number };
    err.statusCode = opts.statusCode;
    return err;
  },
);

vi.stubGlobal("getHeader", mockGetHeader);
vi.stubGlobal("createError", mockCreateError);

function makeEvent(method = "POST") {
  return { method } as Parameters<typeof validateOrigin>[0];
}

function makeConfig(siteUrl = "https://cold.global", additionalOrigins = "") {
  return { public: { siteUrl, additionalOrigins } };
}

describe("buildAllowedOrigins", () => {
  const originalEnv = process.env.VERCEL_URL;

  afterEach(() => {
    if (originalEnv === undefined) {
      delete process.env.VERCEL_URL;
    } else {
      process.env.VERCEL_URL = originalEnv;
    }
  });

  it("extracts origin from siteUrl and includes www variant", () => {
    const origins = buildAllowedOrigins(makeConfig("https://cold.global/path"));
    expect(origins).toEqual(["https://cold.global", "https://www.cold.global"]);
  });

  it("extracts origin from www siteUrl and includes non-www variant", () => {
    const origins = buildAllowedOrigins(
      makeConfig("https://www.cold.global/path"),
    );
    expect(origins).toEqual(["https://www.cold.global", "https://cold.global"]);
  });

  it("includes VERCEL_URL when set", () => {
    process.env.VERCEL_URL = "my-app-abc123.vercel.app";
    const origins = buildAllowedOrigins(makeConfig("https://cold.global"));
    expect(origins).toContain("https://cold.global");
    expect(origins).toContain("https://www.cold.global");
    expect(origins).toContain("https://my-app-abc123.vercel.app");
  });

  it("includes additionalOrigins with www variants", () => {
    const origins = buildAllowedOrigins(
      makeConfig("https://cold.global", "https://choiceoflawdataverse.com"),
    );
    expect(origins).toContain("https://cold.global");
    expect(origins).toContain("https://www.cold.global");
    expect(origins).toContain("https://choiceoflawdataverse.com");
    expect(origins).toContain("https://www.choiceoflawdataverse.com");
  });

  it("handles comma-separated additionalOrigins", () => {
    const origins = buildAllowedOrigins(
      makeConfig(
        "https://cold.global",
        "https://choiceoflawdataverse.com, https://example.org",
      ),
    );
    expect(origins).toContain("https://choiceoflawdataverse.com");
    expect(origins).toContain("https://www.choiceoflawdataverse.com");
    expect(origins).toContain("https://example.org");
    expect(origins).toContain("https://www.example.org");
  });

  it("returns empty array when no siteUrl and no VERCEL_URL", () => {
    delete process.env.VERCEL_URL;
    const origins = buildAllowedOrigins(makeConfig(""));
    expect(origins).toEqual([]);
  });
});

describe("validateOrigin", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("skips validation for GET requests", () => {
    expect(() => validateOrigin(makeEvent("GET"), makeConfig())).not.toThrow();
    expect(mockGetHeader).not.toHaveBeenCalled();
  });

  it("skips validation for HEAD requests", () => {
    expect(() => validateOrigin(makeEvent("HEAD"), makeConfig())).not.toThrow();
  });

  it("skips validation for OPTIONS requests", () => {
    expect(() =>
      validateOrigin(makeEvent("OPTIONS"), makeConfig()),
    ).not.toThrow();
  });

  it("allows matching origin", () => {
    mockGetHeader.mockImplementation((_e: unknown, name: string) =>
      name === "origin" ? "https://cold.global" : undefined,
    );
    expect(() =>
      validateOrigin(makeEvent("POST"), makeConfig("https://cold.global")),
    ).not.toThrow();
  });

  it("allows www variant of matching origin", () => {
    mockGetHeader.mockImplementation((_e: unknown, name: string) =>
      name === "origin" ? "https://www.cold.global" : undefined,
    );
    expect(() =>
      validateOrigin(makeEvent("POST"), makeConfig("https://cold.global")),
    ).not.toThrow();
  });

  it("allows additional origin alias", () => {
    mockGetHeader.mockImplementation((_e: unknown, name: string) =>
      name === "origin" ? "https://choiceoflawdataverse.com" : undefined,
    );
    expect(() =>
      validateOrigin(
        makeEvent("POST"),
        makeConfig("https://cold.global", "https://choiceoflawdataverse.com"),
      ),
    ).not.toThrow();
  });

  it("blocks mismatched origin", () => {
    mockGetHeader.mockImplementation((_e: unknown, name: string) =>
      name === "origin" ? "https://evil.com" : undefined,
    );
    expect(() => validateOrigin(makeEvent("POST"), makeConfig())).toThrow(
      "Forbidden: Invalid origin",
    );
  });

  it("blocks missing origin on POST", () => {
    mockGetHeader.mockReturnValue(undefined);
    expect(() => validateOrigin(makeEvent("POST"), makeConfig())).toThrow(
      "Forbidden: Missing origin",
    );
  });

  it("blocks malformed origin", () => {
    mockGetHeader.mockImplementation((_e: unknown, name: string) =>
      name === "origin" ? "not-a-url" : undefined,
    );
    expect(() => validateOrigin(makeEvent("POST"), makeConfig())).toThrow(
      "Forbidden: Invalid origin",
    );
  });

  it("blocks host-header spoofing attempt", () => {
    mockGetHeader.mockImplementation((_e: unknown, name: string) => {
      if (name === "origin") return "https://evil.com";
      if (name === "host") return "evil.com";
      return undefined;
    });
    expect(() => validateOrigin(makeEvent("POST"), makeConfig())).toThrow(
      "Forbidden: Invalid origin",
    );
  });

  it("does not fall back to referer header", () => {
    mockGetHeader.mockImplementation((_e: unknown, name: string) =>
      name === "referer" ? "https://cold.global" : undefined,
    );
    expect(() => validateOrigin(makeEvent("POST"), makeConfig())).toThrow(
      "Forbidden: Missing origin",
    );
  });
});
