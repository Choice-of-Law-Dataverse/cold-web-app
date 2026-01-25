import { computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { SearchRequest, TableName } from "@/types/api";

const fetchNumberCount = async (tableName: TableName) => {
  if (!tableName) {
    return 0;
  }

  const { apiClient } = useApiClient();

  const body: SearchRequest = {
    search_string: "",
    filters: [
      {
        column: "tables",
        values: [tableName],
      },
    ],
  };

  const data = await apiClient<{ total_matches?: number }>("/search/", {
    body,
  });
  return data.total_matches ?? 0;
};

export function useNumberCount(tableName: Ref<TableName>) {
  return useQuery({
    queryKey: ["numberCount", tableName],
    queryFn: () => fetchNumberCount(tableName.value),
    enabled: computed(() => !!tableName.value),
  });
}
