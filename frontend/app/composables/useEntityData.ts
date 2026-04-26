import {
  computed,
  toValue,
  type ComputedRef,
  type MaybeRefOrGetter,
  type Ref,
} from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import {
  getEntityConfig,
  type EntityBasePath,
  type EntityConfig,
  type ProcessedEntity,
  type ProcessedEntityMap,
} from "@/config/entityRegistry";
import type { TableName } from "@/types/api";

interface EntityDataResult<T> {
  data: ComputedRef<T | null>;
  isLoading: Ref<boolean>;
  error: Ref<Error | null>;
  config: ComputedRef<EntityConfig | undefined>;
}

export function useEntityData<T extends EntityBasePath>(
  basePath: MaybeRefOrGetter<T>,
  coldId: MaybeRefOrGetter<string>,
): EntityDataResult<ProcessedEntityMap[T]>;
export function useEntityData(
  basePath: MaybeRefOrGetter<string | undefined>,
  coldId: MaybeRefOrGetter<string>,
): EntityDataResult<ProcessedEntity>;
export function useEntityData(
  basePath: MaybeRefOrGetter<string | undefined>,
  coldId: MaybeRefOrGetter<string>,
): EntityDataResult<ProcessedEntity> {
  const { client } = useApiClient();

  const config = computed(() => {
    const bp = toValue(basePath);
    return bp ? getEntityConfig(bp) : undefined;
  });

  const resolvedTable = computed((): TableName | undefined => {
    const cfg = config.value;
    if (!cfg) return undefined;
    const id = toValue(coldId);
    if (cfg.table === "Answers" && !id.includes("_")) {
      return "Questions";
    }
    return cfg.table;
  });

  const {
    data: rawData,
    isLoading,
    error,
  } = useQuery({
    queryKey: computed(() => ["entity", resolvedTable.value, toValue(coldId)]),
    queryFn: async () => {
      const cfg = config.value;
      const table = resolvedTable.value;
      if (!cfg || !table) return null;
      const { data, error } = await client.GET("/search/details", {
        params: { query: { table, id: toValue(coldId) } },
      });
      if (error) {
        const detail = (error as { detail?: unknown }).detail;
        throw new Error(
          typeof detail === "string" ? detail : "Failed to load entity",
        );
      }
      return cfg.process(data) as ProcessedEntity;
    },
    enabled: computed(() =>
      Boolean(toValue(coldId) && resolvedTable.value && config.value),
    ),
  });

  const data = computed(() => rawData.value ?? null);

  return { data, isLoading, error, config };
}
