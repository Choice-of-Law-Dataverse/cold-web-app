import {
  computed,
  type ComputedRef,
  type MaybeRefOrGetter,
  type Ref,
  toValue,
} from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { TableName, TableResponseMap, TypedFilter } from "@/types/api";
import {
  type Literature,
  processLiterature,
} from "@/types/entities/literature";
import { formatYear } from "@/utils/format";

export async function fetchFullTableData<T extends TableName>(
  table: T,
  filters: TypedFilter<T>[] = [],
): Promise<TableResponseMap[T][]> {
  const { client } = useApiClient();
  const { data, error } = await client.POST("/search/full_table", {
    body: {
      table,
      filters: filters.length
        ? filters.map((f) => ({
            column: String(f.column),
            value: String(f.value),
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
  const { filters, process, select, enabled } = options;

  return useQuery({
    queryKey: [
      table,
      filters ? filters.map((f) => f.value).join(",") : undefined,
    ],
    queryFn: async () => {
      const data = await fetchFullTableData(table, filters);
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
  const { process, select, enabled } = options;

  return useQuery({
    queryKey: computed(() => [
      table,
      filters.value.map((f) => f.value).join(","),
    ]),
    queryFn: async () => {
      const data = await fetchFullTableData(table, filters.value);
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
    { column: "Jurisdiction" as const, value: jurisdiction.value },
  ]);

  return useFullTableWithFilters<"Literature", Literature>(
    "Literature",
    filters,
    {
      process: processLiterature,
      enabled: () => Boolean(jurisdiction.value),
    },
  );
}
