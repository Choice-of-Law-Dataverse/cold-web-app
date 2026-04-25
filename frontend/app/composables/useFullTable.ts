import {
  computed,
  type ComputedRef,
  type MaybeRefOrGetter,
  type Ref,
  toValue,
} from "vue";
import { useQuery } from "@tanstack/vue-query";
import type createClient from "openapi-fetch";
import { useApiClient } from "@/composables/useApiClient";
import type { TableName, TableResponseMap, TypedFilter } from "@/types/api";
import type { paths } from "@/types/api-schema";
import {
  type LiteratureDisplay,
  processLiteratureRecord,
} from "@/types/entities/literature";
import { formatYear } from "@/utils/format";

type ApiClient = ReturnType<typeof createClient<paths>>;

export interface FullTableQueryParams {
  limit?: number;
  orderBy?: string;
  orderDir?: "asc" | "desc";
}

export async function fetchFullTableData<T extends TableName>(
  client: ApiClient,
  table: T,
  filters: TypedFilter<T>[] = [],
  params: FullTableQueryParams = {},
): Promise<TableResponseMap[T][]> {
  const { data, error } = await client.POST("/search/full_table", {
    body: {
      table,
      filters: filters.length
        ? filters.map((f) => ({
            column: String(f.column),
            value: f.value,
          }))
        : null,
      response_type: null,
      limit: params.limit ?? null,
      order_by: params.orderBy ?? null,
      order_dir: params.orderDir ?? null,
    },
  });
  if (error) throw error;
  return data as unknown as TableResponseMap[T][];
}

interface UseFullTableOptions<
  T extends TableName,
  TProcessed,
  TSelected = TProcessed[],
> extends FullTableQueryParams {
  filters?: TypedFilter<T>[];
  process?: (raw: TableResponseMap[T]) => TProcessed;
  select?: (data: TProcessed[]) => TSelected;
  enabled?: MaybeRefOrGetter<boolean>;
}

export function useFullTable<
  T extends TableName,
  TProcessed = TableResponseMap[T],
  TSelected = TProcessed[],
>(table: T, options: UseFullTableOptions<T, TProcessed, TSelected> = {}) {
  const { client } = useApiClient();
  const { filters, process, select, enabled, limit, orderBy, orderDir } =
    options;

  return useQuery({
    queryKey: [
      table,
      filters ? filters.map((f) => f.value).join(",") : undefined,
      limit ?? null,
      orderBy ?? null,
      orderDir ?? null,
    ],
    queryFn: async () => {
      const data = await fetchFullTableData(client, table, filters, {
        limit,
        orderBy,
        orderDir,
      });
      if (process) {
        return data.map(process);
      }
      return data as TProcessed[];
    },
    select,
    enabled:
      enabled !== undefined ? computed(() => toValue(enabled)) : undefined,
  });
}

export function useFullTableWithFilters<
  T extends TableName,
  TProcessed = TableResponseMap[T],
  TSelected = TProcessed[],
>(
  table: T,
  filters: ComputedRef<TypedFilter<T>[]>,
  options: Omit<UseFullTableOptions<T, TProcessed, TSelected>, "filters"> = {},
) {
  const { client } = useApiClient();
  const { process, select, enabled, limit, orderBy, orderDir } = options;

  return useQuery({
    queryKey: computed(() => [
      table,
      filters.value.map((f) => f.value).join(","),
      limit ?? null,
      orderBy ?? null,
      orderDir ?? null,
    ]),
    queryFn: async () => {
      const data = await fetchFullTableData(client, table, filters.value, {
        limit,
        orderBy,
        orderDir,
      });
      if (process) {
        return data.map(process);
      }
      return data as TProcessed[];
    },
    select,
    enabled:
      enabled !== undefined ? computed(() => toValue(enabled)) : undefined,
  });
}

export function useQuestions() {
  return useFullTable("Questions");
}

export function useInternationalLegalProvisions() {
  return useFullTable("International Legal Provisions", {
    select: (data) => {
      return data.slice().sort((a, b) => {
        const aOrder = Number(a.rankingDisplayOrder) || 0;
        const bOrder = Number(b.rankingDisplayOrder) || 0;
        return aOrder - bOrder;
      });
    },
  });
}

export function useLeadingCases(options: { limit?: number } = {}) {
  const { limit } = options;
  return useFullTable("Court Decisions", {
    filters: [{ column: "caseRank", value: 10 }],
    limit,
    orderBy: limit ? "publicationDateIso" : undefined,
    orderDir: limit ? "desc" : undefined,
    select: (data) => {
      return data.sort(
        (a, b) =>
          (formatYear(b.publicationDateIso) ?? 0) -
          (formatYear(a.publicationDateIso) ?? 0),
      );
    },
  });
}

export function useLiteratureByJurisdiction(jurisdiction: Ref<string>) {
  const filters = computed(() => [
    { column: "jurisdiction" as const, value: jurisdiction.value },
  ]);

  return useFullTableWithFilters<"Literature", LiteratureDisplay>(
    "Literature",
    filters,
    {
      process: processLiteratureRecord,
      enabled: () => Boolean(jurisdiction.value),
    },
  );
}
