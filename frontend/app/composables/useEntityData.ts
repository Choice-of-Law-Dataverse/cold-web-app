import {
  computed,
  toValue,
  type ComputedRef,
  type MaybeRefOrGetter,
  type Ref,
} from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useRequestEvent } from "#imports";
import { setResponseStatus } from "h3";
import { useApiClient } from "@/composables/useApiClient";
import { useServerPrefetch } from "@/composables/useServerPrefetch";
import {
  getEntityConfig,
  type EntityBasePath,
  type EntityConfig,
  type ProcessedEntity,
  type ProcessedEntityMap,
} from "@/config/entityRegistry";
import type { TableName } from "@/types/api";

/** Raised when the backend has no record for the requested id. */
export class EntityNotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "EntityNotFoundError";
  }
}

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
    suspense,
  } = useQuery({
    queryKey: computed(() => ["entity", resolvedTable.value, toValue(coldId)]),
    queryFn: async () => {
      const cfg = config.value;
      const table = resolvedTable.value;
      if (!cfg || !table) return null;
      const { data, error, response } = await client.GET("/search/details", {
        params: { query: { table, id: toValue(coldId) } },
      });
      if (error) {
        const detail = (error as { detail?: unknown }).detail;
        const message =
          typeof detail === "string" ? detail : "Failed to load entity";
        if (response?.status === 404) {
          throw new EntityNotFoundError(message);
        }
        throw new Error(message);
      }
      return cfg.process(data) as ProcessedEntity;
    },
    retry: (failureCount, err) => {
      if (err instanceof EntityNotFoundError) return false;
      if (import.meta.server) return failureCount < 1;
      if (import.meta.dev) return false;
      return failureCount < 3;
    },
    enabled: computed(() =>
      Boolean(toValue(coldId) && resolvedTable.value && config.value),
    ),
  });

  /**
   * Captured during setup: the prefetch callback runs in a detached async
   * context where `useRequestEvent` can no longer find the Nuxt instance.
   *
   * Only the status code is changed. `showError` is deliberately not used —
   * `onServerPrefetch` runs after the layout has rendered, so it produces a
   * stripped error page. Letting the page render its own not-found state keeps
   * the navigation and gives crawlers a correct 404 either way.
   */
  const requestEvent = import.meta.server ? useRequestEvent() : null;

  useServerPrefetch(suspense, (err) => {
    if (!(err instanceof EntityNotFoundError)) return;
    if (requestEvent) setResponseStatus(requestEvent, 404);
  });

  const data = computed(() => rawData.value ?? null);

  return { data, isLoading, error, config };
}
