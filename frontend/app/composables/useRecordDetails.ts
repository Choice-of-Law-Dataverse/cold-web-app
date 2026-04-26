import { computed, type Ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import type createClient from "openapi-fetch";
import { useApiClient } from "@/composables/useApiClient";
import type { TableName, TableDetailMap } from "@/types/api";
import type { paths } from "@/types/api-schema";
import { processQuestion } from "@/types/entities/question";

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

/**
 * Fetches answer or question details based on ID format.
 * IDs containing "_" (e.g., "CH_Q1") are Answers; others are Questions.
 */
export function useAnswer(id: Ref<string | number>) {
  const { client } = useApiClient();
  const table = computed(() =>
    String(id.value).includes("_") ? "Answers" : "Questions",
  );

  return useQuery({
    queryKey: computed(() => [table.value, id.value]),
    queryFn: async () => {
      const { data, error } = await client.GET("/search/details", {
        params: { query: { table: table.value, id: String(id.value) } },
      });
      if (error) throw error;
      return processQuestion(data as Parameters<typeof processQuestion>[0]);
    },
    enabled: computed(() => Boolean(id.value)),
  });
}
