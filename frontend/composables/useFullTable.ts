import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { FullTableRequest, TableName } from "~/types/api";

async function fetchFullTableData<T>(
  table: TableName,
  filters: FullTableRequest["filters"] = [],
): Promise<T[]> {
  const { apiClient } = useApiClient();
  const body: FullTableRequest = { table, filters };

  return await apiClient("/search/full_table", { body });
}

type Options<T> =
  | Partial<{
      select: (data: T[]) => T[];
      filters: FullTableRequest["filters"];
    }>
  | undefined;

export function useFullTable<T = Record<string, unknown>>(
  table: TableName,
  { select, filters }: Options<T> = {},
) {
  return useQuery({
    queryKey: [
      table,
      filters ? filters.map((f) => f.value).join(",") : undefined,
    ],
    queryFn: () => fetchFullTableData<T>(table, filters),
    select,
  });
}
