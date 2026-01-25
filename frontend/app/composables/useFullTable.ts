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

/**
 * Fetch full table data directly (for use with useQueries or custom patterns).
 * Filters are type-safe - column names are validated against the table's response type.
 */
export async function fetchFullTableData<T extends TableName>(
  table: T,
  filters: TypedFilter<T>[] = [],
): Promise<TableResponseMap[T][]> {
  const { apiClient } = useApiClient();
  return await apiClient("/search/full_table", { body: { table, filters } });
}

interface UseFullTableOptions<
  T extends TableName,
  TProcessed,
  TSelected = TProcessed[],
> {
  /** Type-safe filters - column names are validated against the table's response type */
  filters?: TypedFilter<T>[];
  /** Transform each item from raw response to processed type (applied during fetch) */
  process?: (raw: TableResponseMap[T]) => TProcessed;
  /** Post-process the entire result array (applied by TanStack Query's select) */
  select?: (data: TProcessed[]) => TSelected;
  /** Whether the query is enabled */
  enabled?: MaybeRefOrGetter<boolean>;
}

/**
 * Fetch full table data with type-safe filters and optional processing.
 *
 * @example
 * // Basic usage - returns raw response type
 * const { data } = useFullTable("Court Decisions");
 *
 * @example
 * // With processing - transforms each item
 * const { data } = useFullTable("Court Decisions", {
 *   process: processCourtDecision,
 * });
 *
 * @example
 * // With type-safe filters
 * const { data } = useFullTable("Court Decisions", {
 *   filters: [{ column: "Case Rank", value: 10 }],
 * });
 */
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

/**
 * Fetch full table data with reactive filters.
 * Use this when filters depend on reactive state.
 */
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

// Entity-specific composables

export function useQuestions() {
  return useFullTable("Questions");
}

export function useInternationalLegalProvisions() {
  return useFullTable("International Legal Provisions", {
    select: (data) => {
      return data.slice().sort((a, b) => {
        const aOrder = Number(a["Ranking__Display_Order_"]) || 0;
        const bOrder = Number(b["Ranking__Display_Order_"]) || 0;
        return aOrder - bOrder;
      });
    },
  });
}

export function useLeadingCases() {
  return useFullTable("Court Decisions", {
    filters: [{ column: "Case Rank", value: 10 }],
    select: (data) => {
      return data
        .filter(
          (entry) =>
            entry["Case Rank"] === "10" || Number(entry["Case Rank"]) === 10,
        )
        .sort(
          (a, b) =>
            Number(formatYear(b["Publication Date ISO"] || "")) -
            Number(formatYear(a["Publication Date ISO"] || "")),
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
