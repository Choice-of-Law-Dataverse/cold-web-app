import { afterEach, describe, expect, it, vi } from "vitest";
import {
  createMemoryHistory,
  createRouter,
  NavigationFailureType,
} from "vue-router";
import {
  createWebMcpTools,
  getWebMcpContext,
  registerWebMcpTools,
} from "./webMcp";
import type { WebMcpContext } from "./webMcp";
import type { useApiClient } from "@/composables/useApiClient";

afterEach(() => {
  vi.restoreAllMocks();
  Reflect.deleteProperty(document, "modelContext");
  Reflect.deleteProperty(navigator, "modelContext");
});

function setup() {
  const get = vi
    .fn()
    .mockResolvedValue({ data: { results: [], totalMatches: 0 } });
  const push = vi.fn().mockResolvedValue(undefined);
  const client = { GET: get } as unknown as ReturnType<
    typeof useApiClient
  >["client"];
  const tools = createWebMcpTools(client, { push });
  const tool = (name: string) => tools.find((entry) => entry.name === name)!;
  return { client, get, push, tools, tool };
}

function setupNavigation() {
  const { client } = setup();
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: "/court-decision/:coldId", component: {} }],
  });
  const tool = createWebMcpTools(client, router).find(
    ({ name }) => name === "open_cold_record",
  )!;
  return { router, tool };
}

describe("WebMCP", () => {
  it("is unavailable in browsers without the API", () => {
    expect(getWebMcpContext()).toBeUndefined();
  });

  it("prefers the document API and falls back to navigator", () => {
    const current = { registerTool: vi.fn() };
    const legacy = { registerTool: vi.fn() };
    Object.defineProperty(navigator, "modelContext", {
      value: legacy,
      configurable: true,
    });
    expect(getWebMcpContext()).toBe(legacy);
    Object.defineProperty(document, "modelContext", {
      value: current,
      configurable: true,
    });
    expect(getWebMcpContext()).toBe(current);
  });

  it("registers every tool and aborts their registration signals on cleanup", () => {
    const registerTool = vi.fn().mockResolvedValue(undefined);
    const { tools } = setup();
    const cleanup = registerWebMcpTools({ registerTool }, tools);
    expect(registerTool).toHaveBeenCalledTimes(tools.length);
    for (const [tool, options] of registerTool.mock.calls) {
      expect(tools).toContain(tool);
      expect(options.signal.aborted).toBe(false);
    }
    cleanup();
    for (const [, options] of registerTool.mock.calls) {
      expect(options.signal.aborted).toBe(true);
    }
  });

  it("handles rejected and synchronous registrations without stopping other tools", async () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const { tools } = setup();
    const registerTool = vi
      .fn()
      .mockRejectedValueOnce(new Error("Denied"))
      .mockImplementationOnce(() => {
        throw new Error("Duplicate");
      })
      .mockResolvedValue(undefined);
    registerWebMcpTools({ registerTool }, tools);
    await vi.waitFor(() => expect(warn).toHaveBeenCalledTimes(2));
    expect(registerTool).toHaveBeenCalledTimes(tools.length);
  });

  it("does not warn about an expected registration abort", async () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const { tools } = setup();
    const context: WebMcpContext = {
      registerTool: (_tool, { signal }) =>
        new Promise((_, reject) => {
          signal.addEventListener("abort", () => reject(signal.reason));
        }),
    };
    registerWebMcpTools(context, tools)();
    await Promise.resolve();
    expect(warn).not.toHaveBeenCalled();
  });

  it("searches with filters and pagination through the existing API client", async () => {
    const { tool, get } = setup();
    const result = await tool("search_cold").execute({
      query: " party autonomy ",
      jurisdiction: "Switzerland",
      theme: "Public policy",
      page: 2,
      pageSize: 20,
    });
    expect(get).toHaveBeenCalledWith("/search/", {
      params: {
        query: {
          search_string: "party autonomy",
          jurisdictions: ["Switzerland"],
          themes: ["Public policy"],
          page: 2,
          page_size: 20,
        },
      },
    });
    expect(result).toEqual({ results: [], totalMatches: 0 });
  });

  it("rejects invalid search arguments before making requests", async () => {
    const { tool, get } = setup();
    for (const input of [
      { query: " " },
      { query: "law", page: 0 },
      { query: "law", pageSize: 101 },
    ]) {
      await expect(tool("search_cold").execute(input)).rejects.toThrow();
    }
    expect(get).not.toHaveBeenCalled();
  });

  it("retrieves a record using the registry table mapping", async () => {
    const { tool, get } = setup();
    await tool("get_cold_record").execute({
      entityPath: "/court-decision",
      coldId: "CD-CHE-42",
    });
    expect(get).toHaveBeenCalledWith("/search/details", {
      params: { query: { table: "Court Decisions", id: "CD-CHE-42" } },
    });
  });

  it.each([
    [
      "/domestic-legal-provision",
      "Domestic Legal Provisions",
      "DI-CHE-1 Art. 116(2)",
    ],
    [
      "/regional-legal-provision",
      "Regional Legal Provisions",
      "RI-EU-1 Article 3(1)",
    ],
    [
      "/international-legal-provision",
      "International Legal Provisions",
      "II-HCC-1 Art. 2/3",
    ],
  ])(
    "retrieves %s using its complete provision identifier",
    async (entityPath, table, coldId) => {
      const { tool, get } = setup();
      await tool("get_cold_record").execute({ entityPath, coldId });
      expect(get).toHaveBeenCalledWith("/search/details", {
        params: { query: { table, id: coldId } },
      });
    },
  );

  it.each(["", " ", "x".repeat(129)])(
    "rejects an invalid retrieval identifier %j",
    async (coldId) => {
      const { tool, get } = setup();
      await expect(
        tool("get_cold_record").execute({
          entityPath: "/court-decision",
          coldId,
        }),
      ).rejects.toThrow();
      expect(get).not.toHaveBeenCalled();
    },
  );

  it("accepts dotted question identifiers and blocks entities without detail pages", async () => {
    const { tool, push } = setup();
    await tool("open_cold_record").execute({
      entityPath: "/question",
      coldId: "30.2-AoC",
    });
    expect(push).toHaveBeenCalledWith("/question/30.2-AoC");
    push.mockClear();
    await expect(
      tool("open_cold_record").execute({
        entityPath: "/domestic-legal-provision",
        coldId: "DLP-1",
      }),
    ).rejects.toThrow("no detail page");
    expect(push).not.toHaveBeenCalled();
  });

  it("distinguishes comparative questions from jurisdiction answers", async () => {
    const { tool, get } = setup();
    await tool("get_cold_record").execute({
      entityPath: "/question",
      coldId: "30.2-AoC",
    });
    expect(get).toHaveBeenLastCalledWith("/search/details", {
      params: { query: { table: "Questions", id: "30.2-AoC" } },
    });
    await tool("get_cold_record").execute({
      entityPath: "/question",
      coldId: "CHE_30.2-AoC",
    });
    expect(get).toHaveBeenLastCalledWith("/search/details", {
      params: { query: { table: "Answers", id: "CHE_30.2-AoC" } },
    });
  });

  it("propagates API errors to the calling agent", async () => {
    const { tool, get } = setup();
    get.mockResolvedValue({ error: new Error("Unavailable") });
    await expect(tool("search_cold").execute({ query: "law" })).rejects.toThrow(
      "Unavailable",
    );
    await expect(
      tool("get_cold_record").execute({
        entityPath: "/court-decision",
        coldId: "CD-CHE-42",
      }),
    ).rejects.toThrow("Unavailable");
  });

  it("navigates to a public record and rejects arbitrary paths and URLs", async () => {
    const { tool, push } = setup();
    await expect(
      tool("open_cold_record").execute({
        entityPath: "/court-decision",
        coldId: "CD-CHE-42",
      }),
    ).resolves.toEqual({ path: "/court-decision/CD-CHE-42" });
    expect(push).toHaveBeenCalledWith("/court-decision/CD-CHE-42");
    push.mockClear();
    for (const input of [
      { entityPath: "/moderation", coldId: "42" },
      { entityPath: "https://example.com", coldId: "42" },
      { entityPath: "/court-decision", coldId: "../new" },
    ]) {
      await expect(tool("open_cold_record").execute(input)).rejects.toThrow();
    }
    expect(push).not.toHaveBeenCalled();
  });

  it("succeeds when asked to open the current record again", async () => {
    const { router, tool } = setupNavigation();
    const input = { entityPath: "/court-decision", coldId: "CD-CHE-42" };
    await expect(tool.execute(input)).resolves.toEqual({
      path: "/court-decision/CD-CHE-42",
    });
    await expect(tool.execute(input)).resolves.toEqual({
      path: "/court-decision/CD-CHE-42",
    });
    expect(router.currentRoute.value.path).toBe("/court-decision/CD-CHE-42");
  });

  it("still rejects navigation aborted by a guard", async () => {
    const { router, tool } = setupNavigation();
    router.beforeEach(() => false);
    await expect(
      tool.execute({ entityPath: "/court-decision", coldId: "CD-CHE-42" }),
    ).rejects.toMatchObject({ type: NavigationFailureType.aborted });
  });

  it("still rejects navigation cancelled by a newer request", async () => {
    const { router, tool } = setupNavigation();
    let releaseGuard!: () => void;
    let guardStarted!: () => void;
    const started = new Promise<void>((resolve) => {
      guardStarted = resolve;
    });
    router.beforeEach((to) => {
      if (to.params.coldId !== "CD-CHE-42") return;
      guardStarted();
      return new Promise<void>((resolve) => {
        releaseGuard = resolve;
      });
    });
    const navigation = tool.execute({
      entityPath: "/court-decision",
      coldId: "CD-CHE-42",
    });
    const rejected = expect(navigation).rejects.toMatchObject({
      type: NavigationFailureType.cancelled,
    });
    await started;
    await tool.execute({ entityPath: "/court-decision", coldId: "CD-CHE-43" });
    releaseGuard();
    await rejected;
    expect(router.currentRoute.value.path).toBe("/court-decision/CD-CHE-43");
  });
});
