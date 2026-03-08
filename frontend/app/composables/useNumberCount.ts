import { computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { TableName } from "@/types/api";

const fetchNumberCount = async (tableName: TableName) => {
  if (!tableName) {
    return 0;
  }

  const { client } = useApiClient();

  const { data, error } = await client.POST("/search/", {
    body: {
      search_string: "",
      filters: [
        {
          column: "tables",
          values: [tableName],
        },
      ],
      page: 1,
      page_size: 1,
      sort_by_date: false,
      response_type: null,
    },
  });

  if (error) throw error;
  return data.totalMatches ?? 0;
};

export function useNumberCount(tableName: Ref<TableName>) {
  return useQuery({
    queryKey: ["numberCount", tableName],
    queryFn: () => fetchNumberCount(tableName.value),
    enabled: computed(() => !!tableName.value),
  });
}
