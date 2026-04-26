import { computed, type Ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import type createClient from "openapi-fetch";
import { useApiClient } from "@/composables/useApiClient";
import type { TableName, TableDetailMap } from "@/types/api";
import type { paths } from "@/types/api-schema";

type ApiClient = ReturnType<typeof createClient<paths>>;

async function fetchRecordDetails<
  T extends TableName,
  TProcessed = TableDetailMap[T],
>(
  client: ApiClient,
  table: T,
  id: string | number,
  process?: (raw: TableDetailMap[T]) => TProcessed,
) {
  const { data, error } = await client.GET("/search/details", {
    params: { query: { table, id: String(id) } },
  });
  if (error) throw error;
  const raw = data as unknown as TableDetailMap[T];
  return process ? process(raw) : (raw as unknown as TProcessed);
}

export function useRecordDetails<
  T extends TableName,
  TProcessed = TableDetailMap[T],
>(
  table: T,
  id: Ref<string | number>,
  process?: (raw: TableDetailMap[T]) => TProcessed,
) {
  const { client } = useApiClient();

  return useQuery({
    queryKey: computed(() => [table, id.value]),
    queryFn: () => fetchRecordDetails(client, table, id.value, process),
    enabled: computed(() => Boolean(id.value)),
  });
}
