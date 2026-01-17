import { computed, type Ref } from "vue";
import { useQuery, useQueries } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { TableName } from "@/types/api";

async function fetchRecordDetails<T>(table: TableName, id: string | number) {
  const { apiClient } = useApiClient();
  return await apiClient<T>("/search/details", { body: { table, id } });
}

async function fetchAndProcess<TRaw, TProcessed>(
  table: TableName,
  id: string | number,
  process: (raw: TRaw) => TProcessed,
) {
  const { apiClient } = useApiClient();
  const raw = await apiClient<TRaw>("/search/details", { body: { table, id } });
  return process(raw);
}

/** Simple fetch without transformation */
export function useRecordDetails<T>(
  table: Ref<TableName>,
  id: Ref<string | number>,
) {
  return useQuery({
    queryKey: computed(() => [table.value, id.value]),
    queryFn: () => fetchRecordDetails<T>(table.value, id.value),
    enabled: computed(() => Boolean(table.value && id.value)),
  });
}

/** Fetch with transformation applied before caching */
export function useRecordDetailsProcessed<TRaw, TProcessed>(
  table: Ref<TableName>,
  id: Ref<string | number>,
  process: (raw: TRaw) => TProcessed,
) {
  return useQuery({
    queryKey: computed(() => [table.value, id.value, "processed"]),
    queryFn: () => fetchAndProcess<TRaw, TProcessed>(table.value, id.value, process),
    enabled: computed(() => Boolean(table.value && id.value)),
  });
}

export function useRecordDetailsList<T>(
  table: Ref<TableName>,
  ids: Ref<Array<string | number>>,
) {
  const queries = computed(() => {
    const list = ids.value || [];
    return list.map((id) => ({
      queryKey: [table.value, id],
      queryFn: () => fetchRecordDetails<T>(table.value, id),
      enabled: Boolean(table.value && id),
    }));
  });

  const results = useQueries({ queries });

  const data = computed(() => results.value.map((r) => r.data));
  const isLoading = computed(() => results.value.some((r) => r.isLoading));
  const hasError = computed(() => results.value.some((r) => r.isError));
  const error = computed(() => results.value.find((r) => r.isError)?.error);

  return { data, isLoading, hasError, error };
}
