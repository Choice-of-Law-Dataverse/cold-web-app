import { computed, type Ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";

interface JurisdictionCount {
  jurisdiction: string;
  n: number;
}

async function fetchCountByJurisdiction(tableName: string) {
  const { apiClient } = useApiClient();
  return await apiClient<JurisdictionCount[]>(
    `/statistics/count-by-jurisdiction?table=${encodeURIComponent(tableName)}`,
    { method: "GET" },
  );
}

export function useCountByJurisdiction(tableName: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ["countByJurisdiction", tableName.value]),
    queryFn: () => fetchCountByJurisdiction(tableName.value),
    enabled: computed(() => Boolean(tableName.value)),
  });
}
