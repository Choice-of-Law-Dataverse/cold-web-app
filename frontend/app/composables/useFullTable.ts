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

export async function fetchFullTableData<T extends TableName>(
  client: ApiClient,
  table: T,
  filters: TypedFilter<T>[] = [],
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
    },
  });
  if (error) throw error;
  return data as unknown as TableResponseMap[T][];
}

interface UseFullTableOptions<
  T extends TableName,
  TProcessed,
  TSelected = TProcessed[],
> {
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
  const { filters, process, select, enabled } = options;

  return useQuery({
    queryKey: [
      table,
      filters ? filters.map((f) => f.value).join(",") : undefined,
    ],
    queryFn: async () => {
      const data = await fetchFullTableData(client, table, filters);
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
  const { process, select, enabled } = options;

  return useQuery({
    queryKey: computed(() => [
      table,
      filters.value.map((f) => f.value).join(","),
    ]),
    queryFn: async () => {
      const data = await fetchFullTableData(client, table, filters.value);
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

export function useLeadingCases() {
  return useFullTable("Court Decisions", {
    filters: [{ column: "caseRank", value: 10 }],
    select: (data) => {
      return data
        .filter(
          (entry) => entry.caseRank === "10" || Number(entry.caseRank) === 10,
        )
        .sort(
          (a, b) =>
            Number(formatYear(b.publicationDateIso || "")) -
            Number(formatYear(a.publicationDateIso || "")),
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
