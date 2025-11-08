import { computed, type Ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";

interface JurisdictionCount {
  jurisdiction: string;
  n: number;
}

async function fetchCountByJurisdiction(tableName: string, limit?: number) {
  const { apiClient } = useApiClient();
  const params = new URLSearchParams({ table: tableName });
  if (limit) {
    params.append("limit", limit.toString());
  }
  return await apiClient<JurisdictionCount[]>(
    `/statistics/count-by-jurisdiction?${params.toString()}`,
    { method: "GET" },
  );
}

export function useCountByJurisdiction(
  tableName: Ref<string>,
  limit?: Ref<number | undefined>,
) {
  return useQuery({
    queryKey: computed(() => [
      "countByJurisdiction",
      tableName.value,
      limit?.value,
    ]),
    queryFn: () => fetchCountByJurisdiction(tableName.value, limit?.value),
    enabled: computed(() => Boolean(tableName.value)),
  });
}
