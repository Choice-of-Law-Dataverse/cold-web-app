import { computed, type MaybeRefOrGetter, toValue } from "vue";
import { keepPreviousData, useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { components } from "@/types/api-schema";

type Schemas = components["schemas"];

export type EntitySlug =
  | "arbitral-awards"
  | "arbitral-institutions"
  | "arbitral-rules"
  | "court-decisions"
  | "domestic-instruments"
  | "international-instruments"
  | "jurisdictions"
  | "literature"
  | "questions"
  | "regional-instruments"
  | "specialists";

export type EntityRelationMap = {
  "arbitral-awards": Schemas["ArbitralAwardRelation"];
  "arbitral-institutions": Schemas["ArbitralInstitutionRelation"];
  "arbitral-rules": Schemas["ArbitralRuleRelation"];
  "court-decisions": Schemas["CourtDecisionRelation"];
  "domestic-instruments": Schemas["DomesticInstrumentRelation"];
  "international-instruments": Schemas["InternationalInstrumentRelation"];
  jurisdictions: Schemas["JurisdictionRelation"];
  literature: Schemas["LiteratureRelation"];
  questions: Schemas["QuestionRelation"];
  "regional-instruments": Schemas["RegionalInstrumentRelation"];
  specialists: Schemas["SpecialistRelation"];
};

export interface EntityListPage<S extends EntitySlug> {
  items: EntityRelationMap[S][];
  total: number;
  page: number;
  pageSize: number;
}

export interface UseEntityListParams {
  jurisdiction?: MaybeRefOrGetter<string | null | undefined>;
  caseRank?: MaybeRefOrGetter<string | null | undefined>;
  page?: MaybeRefOrGetter<number>;
  pageSize?: MaybeRefOrGetter<number>;
  orderBy?: MaybeRefOrGetter<string | null | undefined>;
  orderDir?: MaybeRefOrGetter<"asc" | "desc" | null | undefined>;
  enabled?: MaybeRefOrGetter<boolean>;
}

export function useEntityList<S extends EntitySlug>(
  slug: S,
  params: UseEntityListParams = {},
) {
  const { client } = useApiClient();

  return useQuery({
    queryKey: computed(() => [
      "entityList",
      slug,
      toValue(params.jurisdiction) ?? null,
      toValue(params.caseRank) ?? null,
      toValue(params.page) ?? 1,
      toValue(params.pageSize) ?? 200,
      toValue(params.orderBy) ?? null,
      toValue(params.orderDir) ?? null,
    ]),
    queryFn: async (): Promise<EntityListPage<S>> => {
      const { data, error } = await client.GET("/entities/{slug}", {
        params: {
          path: { slug },
          query: {
            jurisdiction: toValue(params.jurisdiction) || undefined,
            case_rank: toValue(params.caseRank) || undefined,
            page: toValue(params.page) || 1,
            page_size: toValue(params.pageSize) || 200,
            order_by: toValue(params.orderBy) || undefined,
            order_dir: toValue(params.orderDir) || undefined,
          },
        },
      });
      if (error || !data)
        throw error ?? new Error("Empty entity list response");
      return {
        items: data.items as EntityRelationMap[S][],
        total: data.total,
        page: data.page,
        pageSize: data.pageSize,
      };
    },
    placeholderData: keepPreviousData,
    enabled:
      params.enabled !== undefined
        ? computed(() => toValue(params.enabled!))
        : undefined,
  });
}
