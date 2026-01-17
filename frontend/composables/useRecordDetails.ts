import { computed, type Ref } from "vue";
import { useQuery, useQueries } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { TableName } from "@/types/api";

async function fetchRecordDetails<TRaw, TProcessed = TRaw>(
  table: TableName,
  id: string | number,
  process?: (raw: TRaw) => TProcessed,
) {
  const { apiClient } = useApiClient();
  const raw = await apiClient<TRaw>("/search/details", { body: { table, id } });
  return process ? process(raw) : (raw as unknown as TProcessed);
}

export function useRecordDetails<TRaw, TProcessed = TRaw>(
  table: Ref<TableName>,
  id: Ref<string | number>,
  process?: (raw: TRaw) => TProcessed,
) {
  return useQuery({
    queryKey: computed(() => [table.value, id.value]),
    queryFn: () =>
      fetchRecordDetails<TRaw, TProcessed>(table.value, id.value, process),
    enabled: computed(() => Boolean(table.value && id.value)),
  });
}

export function useRecordDetailsList<TRaw, TProcessed = TRaw>(
  table: Ref<TableName>,
  ids: Ref<Array<string | number>>,
  process?: (raw: TRaw) => TProcessed,
) {
  const queries = computed(() => {
    const list = ids.value || [];
    return list.map((id) => ({
      queryKey: [table.value, id],
      queryFn: () =>
        fetchRecordDetails<TRaw, TProcessed>(table.value, id, process),
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
