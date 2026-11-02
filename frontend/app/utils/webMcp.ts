import { z } from "zod";
import type { Router } from "vue-router";
import type { useApiClient } from "@/composables/useApiClient";
import { entityRegistry } from "@/config/entityRegistry";

export interface WebMcpTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
  annotations: { readOnlyHint: boolean };
  execute: (input: unknown) => Promise<unknown>;
}

export interface WebMcpContext {
  registerTool: (
    tool: WebMcpTool,
    options: { signal: AbortSignal },
  ) => Promise<unknown>;
}

export function getWebMcpContext(): WebMcpContext | undefined {
  const current = (document as Document & { modelContext?: WebMcpContext })
    .modelContext;
  if (typeof current?.registerTool === "function") return current;
  const legacy = (navigator as Navigator & { modelContext?: WebMcpContext })
    .modelContext;
  return typeof legacy?.registerTool === "function" ? legacy : undefined;
}

export function registerWebMcpTools(
  context: WebMcpContext,
  tools: WebMcpTool[],
): () => void {
  const controller = new AbortController();
  for (const tool of tools) {
    void (async () => {
      try {
        await context.registerTool(tool, { signal: controller.signal });
      } catch (error) {
        if (!controller.signal.aborted) {
          console.warn(`WebMCP: could not register ${tool.name}`, error);
        }
      }
    })();
  }
  return () => controller.abort();
}

export function createWebMcpTools(
  client: ReturnType<typeof useApiClient>["client"],
  router: Pick<Router, "push">,
): WebMcpTool[] {
  const searchSchema = z.strictObject({
    query: z
      .string()
      .trim()
      .min(1)
      .max(1000)
      .describe("Search words, such as party autonomy or public policy"),
    jurisdiction: z
      .string()
      .max(200)
      .optional()
      .describe("Jurisdiction name, such as Switzerland"),
    theme: z
      .string()
      .max(200)
      .optional()
      .describe("Choice of law theme to filter by"),
    page: z
      .number()
      .int()
      .min(1)
      .default(1)
      .describe("Result page, starting at 1"),
    pageSize: z
      .number()
      .int()
      .min(1)
      .max(100)
      .default(10)
      .describe("Maximum records per page"),
  });
  const recordSchema = z.strictObject({
    entityPath: z
      .enum(Object.keys(entityRegistry) as [string, ...string[]])
      .describe("Entity section for the record"),
    coldId: z
      .string()
      .trim()
      .min(1)
      .max(128)
      .regex(/^[A-Za-z0-9][A-Za-z0-9_.-]*$/)
      .describe(
        "CoLD identifier from search results, such as CD-CHE-42 or 30.2-AoC",
      ),
  });

  return [
    {
      name: "search_cold",
      description:
        "Search the Choice of Law Dataverse for court decisions, legal instruments, literature, arbitral materials and jurisdiction answers. Returns structured records and the total match count.",
      inputSchema: z.toJSONSchema(searchSchema, { io: "input" }),
      annotations: { readOnlyHint: true },
      async execute(input) {
        const { query, jurisdiction, theme, page, pageSize } =
          searchSchema.parse(input);
        const { data, error } = await client.GET("/search/", {
          params: {
            query: {
              search_string: query,
              jurisdictions: jurisdiction ? [jurisdiction] : undefined,
              themes: theme ? [theme] : undefined,
              page,
              page_size: pageSize,
            },
          },
        });
        if (error) throw error;
        return data;
      },
    },
    {
      name: "get_cold_record",
      description:
        "Retrieve a CoLD record and its related entities as structured data. Use an entity section and a CoLD identifier found in search results.",
      inputSchema: z.toJSONSchema(recordSchema),
      annotations: { readOnlyHint: true },
      async execute(input) {
        const { entityPath, coldId } = recordSchema.parse(input);
        const { data, error } = await client.GET("/search/details", {
          params: {
            query: { table: entityRegistry[entityPath]!.table, id: coldId },
          },
        });
        if (error) throw error;
        return data;
      },
    },
    {
      name: "open_cold_record",
      description:
        "Navigate the browser to a CoLD record so the user can read it. Use an entity section and a CoLD identifier found in search results.",
      inputSchema: z.toJSONSchema(recordSchema),
      annotations: { readOnlyHint: true },
      async execute(input) {
        const { entityPath, coldId } = recordSchema.parse(input);
        if (entityRegistry[entityPath]!.hasDetailPage === false) {
          throw new Error(
            "This entity has no detail page. Use get_cold_record instead.",
          );
        }
        const path = `${entityPath}/${encodeURIComponent(coldId)}`;
        const failure = await router.push(path);
        if (failure) throw failure;
        return { path };
      },
    },
  ];
}
