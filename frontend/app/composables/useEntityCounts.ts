import { computed, type MaybeRefOrGetter, toValue } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";

export type EntityCountKey =
  | "answers"
  | "arbitralAwards"
  | "arbitralInstitutions"
  | "arbitralProvisions"
  | "arbitralRules"
  | "courtDecisions"
  | "domesticInstruments"
  | "domesticLegalProvisions"
  | "hcchAnswers"
  | "internationalInstruments"
  | "internationalLegalProvisions"
  | "jurisdictions"
  | "literature"
  | "questions"
  | "regionalInstruments"
  | "regionalLegalProvisions"
  | "specialists";

export type EntityCounts = Partial<Record<EntityCountKey, number>>;

export function useEntityCounts(
  jurisdiction?: MaybeRefOrGetter<string | null | undefined>,
) {
  const { client } = useApiClient();

  return useQuery({
    queryKey: computed(() => ["entityCounts", toValue(jurisdiction) ?? null]),
    queryFn: async (): Promise<EntityCounts> => {
      const { data, error } = await client.GET("/statistics/counts", {
        params: {
          query: {
            jurisdiction: toValue(jurisdiction) || undefined,
          },
        },
      });
      if (error) throw error;
      return (data.counts ?? {}) as EntityCounts;
    },
  });
}
