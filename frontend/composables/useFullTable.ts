import { useQuery, type UseQueriesOptions } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { FullTableRequest, TableName } from "~/types/api";

const fetchFullTableData = async (
  table: TableName,
  filters: FullTableRequest["filters"] = [],
): Promise<any[]> => {
  const { apiClient } = useApiClient();
  const body: FullTableRequest = { table, filters };

  return await apiClient("/search/full_table", { body });
};

type Options =
  | Partial<{
      select: (data: any[]) => any[];
      filters: FullTableRequest["filters"];
    }>
  | undefined;

export function useFullTable(
  table: TableName,
  { select, filters }: Options = {},
) {
  return useQuery({
    queryKey: [
      table,
      filters ? filters.map((f) => f.value).join(",") : undefined,
    ],
    queryFn: () => fetchFullTableData(table, filters),
    select,
  });
}
