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

type ApiClient = ReturnType<typeof createClient<paths>>;

export interface FullTableQueryParams {
  limit?: number;
  orderBy?: string;
  orderDir?: "asc" | "desc";
}

const encodeFilter = <T extends TableName>(filter: TypedFilter<T>): string => {
  const serialized = String(filter.value);
  if (serialized.includes(",")) {
    throw new Error(
      `Filter value for column "${String(filter.column)}" contains a comma; ` +
        "the GET /search/full_table wire format reserves ',' as a multi-value separator.",
    );
  }
  return `${String(filter.column)}:${serialized}`;
};

export async function fetchFullTableData<T extends TableName>(
  client: ApiClient,
  table: T,
  filters: TypedFilter<T>[] = [],
  params: FullTableQueryParams = {},
): Promise<TableResponseMap[T][]> {
  const { data, error } = await client.GET("/search/full_table", {
    params: {
      query: {
        table,
        filter: filters.length ? filters.map(encodeFilter) : undefined,
        limit: params.limit ?? undefined,
        order_by: params.orderBy ?? undefined,
        order_dir: params.orderDir ?? undefined,
      },
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
      filters ? JSON.stringify(filters) : undefined,
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
      JSON.stringify(filters.value),
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
