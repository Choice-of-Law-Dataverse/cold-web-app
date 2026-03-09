import { computed, toValue, type MaybeRefOrGetter } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import { getEntityConfig } from "@/config/entityRegistry";
import type { TableName } from "@/types/api";

export function useEntityData(
  basePath: MaybeRefOrGetter<string | undefined>,
  id: MaybeRefOrGetter<string>,
) {
  const { client } = useApiClient();

  const config = computed(() => {
    const bp = toValue(basePath);
    return bp ? getEntityConfig(bp) : undefined;
  });

  const resolvedTable = computed((): TableName | undefined => {
    const cfg = config.value;
    if (!cfg) return undefined;
    const idVal = toValue(id);
    if (cfg.table === "Answers" && !idVal.includes("_")) {
      return "Questions";
    }
    return cfg.table;
  });

  const {
    data: rawData,
    isLoading,
    error,
  } = useQuery({
    queryKey: computed(() => ["entity", resolvedTable.value, toValue(id)]),
    queryFn: async () => {
      const cfg = config.value;
      const table = resolvedTable.value;
      if (!cfg || !table) return null;
      const { data, error } = await client.POST("/search/details", {
        body: { table, id: toValue(id) },
      });
      if (error) throw error;
      return cfg.process(data);
    },
    enabled: computed(() =>
      Boolean(toValue(id) && resolvedTable.value && config.value),
    ),
  });

  const data = computed(() => rawData.value as Record<string, unknown> | null);

  return { data, isLoading, error, config };
}
