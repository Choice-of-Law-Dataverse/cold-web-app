import { computed, ref, type Ref, type MaybeRefOrGetter } from "vue";
import { useQuery } from "@tanstack/vue-query";
import type createClient from "openapi-fetch";
import { useApiClient } from "@/composables/useApiClient";
import type {
  JurisdictionWithAnswerCoverage,
  JurisdictionCount,
  TableName,
} from "@/types/api";
import type { paths } from "@/types/api-schema";
import { flagUrl } from "@/config/assets";

type ApiClient = ReturnType<typeof createClient<paths>>;

const EMPTY_SET = new Set<string>();
const EMPTY_MAP = new Map<string, ProcessedJurisdiction>();

export interface ProcessedJurisdiction {
  id: number;
  name: string;
  coldId: string;
  legalFamily: string;
  irrelevant?: boolean | null;
  answerCoverage: number;
  label: string;
  avatar: string | undefined;
}

interface JurisdictionsData {
  jurisdictions: ProcessedJurisdiction[];
  knownJurisdictionTerms: Set<string>;
  byName: Map<string, ProcessedJurisdiction>;
  byColdId: Map<string, ProcessedJurisdiction>;
  coveredCountries: Set<string>;
}

function processJurisdiction(
  record: JurisdictionWithAnswerCoverage,
): ProcessedJurisdiction {
  const coldId = record.coldId?.toUpperCase() || "";
  return {
    id: record.id,
    name: record.name || "N/A",
    coldId,
    legalFamily: record.legalFamily || "N/A",
    irrelevant: record.irrelevant,
    answerCoverage: record.answerCoverage ?? 0,
    label: record.name,
    avatar: coldId ? flagUrl(coldId) : undefined,
  };
}

async function fetchAndProcessJurisdictions(
  client: ApiClient,
): Promise<JurisdictionsData> {
  const { data, error } = await client.GET(
    "/statistics/jurisdictions-with-answer-percentage",
  );
  if (error) throw error;

  const jurisdictions = (data as JurisdictionWithAnswerCoverage[])
    .filter((record) => record.irrelevant !== true)
    .map(processJurisdiction);

  const knownJurisdictionTerms = new Set<string>();
  const byName = new Map<string, ProcessedJurisdiction>();
  const byColdId = new Map<string, ProcessedJurisdiction>();
  const coveredCountries = new Set<string>();

  for (const j of jurisdictions) {
    const nameLower = j.name.toLowerCase();
    knownJurisdictionTerms.add(nameLower);
    byName.set(nameLower, j);

    if (j.coldId) {
      knownJurisdictionTerms.add(j.coldId.toLowerCase());
      byColdId.set(j.coldId, j);

      if (j.answerCoverage > 0) {
        coveredCountries.add(j.coldId);
      }
    }
  }

  return {
    jurisdictions,
    knownJurisdictionTerms,
    byName,
    byColdId,
    coveredCountries,
  };
}

export function useJurisdictions(enabled?: MaybeRefOrGetter<boolean>) {
  const { client } = useApiClient();

  const { data, ...rest } = useQuery({
    queryKey: ["jurisdictions-with-answer-percentage"],
    queryFn: () => fetchAndProcessJurisdictions(client),
    enabled,
    staleTime: 1000 * 60 * 30,
    gcTime: 1000 * 60 * 60 * 2,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  return {
    data: computed(() => data.value?.jurisdictions),
    knownJurisdictionTerms: computed(
      () => data.value?.knownJurisdictionTerms ?? EMPTY_SET,
    ),
    byName: computed(() => data.value?.byName ?? EMPTY_MAP),
    byColdId: computed(() => data.value?.byColdId ?? EMPTY_MAP),
    coveredCountries: computed(() => data.value?.coveredCountries ?? EMPTY_SET),
    ...rest,
  };
}

export function useJurisdiction(coldId: Ref<string>) {
  const { byColdId, isLoading, error, isError, isFetching } =
    useJurisdictions();

  const data = computed(() => {
    if (!coldId.value) return undefined;
    return byColdId.value.get(coldId.value.toUpperCase());
  });

  return {
    data,
    isLoading,
    error,
    isError,
    isFetching,
  };
}

export function useJurisdictionLookup(enabled?: MaybeRefOrGetter<boolean>) {
  const {
    data: jurisdictions,
    knownJurisdictionTerms,
    byName,
    byColdId,
    ...rest
  } = useJurisdictions(enabled);

  const getJurisdictionISO = (name: string): string => {
    if (!name) return "default";
    const jurisdiction = byName.value.get(name.toLowerCase());
    return jurisdiction?.coldId?.toUpperCase() || "default";
  };

  const findMatchingJurisdictions = (words: string[]): string[] => {
    if (!jurisdictions.value || words.length === 0) return [];

    return jurisdictions.value
      .filter((j) =>
        words.some((word) => {
          const nameLower = j.name.toLowerCase();
          const codeLower = j.coldId?.toLowerCase() || "";
          return nameLower.includes(word) || codeLower.includes(word);
        }),
      )
      .map((j) => j.name);
  };

  const findJurisdictionByName = (name: string) => {
    if (!name) return undefined;
    return byName.value.get(name.toLowerCase());
  };

  const findJurisdictionByCode = (code: string) => {
    if (!code) return undefined;
    return byColdId.value.get(code.toUpperCase());
  };

  const isJurisdictionTerm = (word: string): boolean => {
    return knownJurisdictionTerms.value.has(word.toLowerCase());
  };

  return {
    ...rest,
    data: jurisdictions,
    knownJurisdictionTerms,
    getJurisdictionISO,
    findMatchingJurisdictions,
    findJurisdictionByName,
    findJurisdictionByCode,
    isJurisdictionTerm,
  };
}

export function useCoveredCountries() {
  const { coveredCountries, isLoading, error, isError, isFetching } =
    useJurisdictions();

  return {
    data: coveredCountries,
    isLoading,
    error,
    isError,
    isFetching,
  };
}

async function fetchCountByJurisdiction(
  client: ApiClient,
  tableName: TableName,
  limit?: number,
) {
  const { data, error } = await client.GET(
    "/statistics/count-by-jurisdiction",
    {
      params: {
        query: { table: tableName, limit: limit ?? undefined },
      },
    },
  );
  if (error) throw error;
  return data as JurisdictionCount[];
}

function useCountByJurisdiction(
  tableName: Ref<TableName>,
  limit?: Ref<number | undefined>,
) {
  const { client } = useApiClient();

  return useQuery({
    queryKey: computed(() => [
      "countByJurisdiction",
      tableName.value,
      limit?.value,
    ]),
    queryFn: () =>
      fetchCountByJurisdiction(client, tableName.value, limit?.value),
    enabled: computed(() => Boolean(tableName.value)),
  });
}

export function useJurisdictionChart() {
  const tableName = ref("Court Decisions" as TableName);
  const limit = ref(6);
  const {
    data: rawData,
    isLoading,
    error,
  } = useCountByJurisdiction(tableName, limit);

  const data = computed(() => {
    if (!rawData.value) return null;

    const xValues = rawData.value.map((item) => item.n);
    const yValues = rawData.value.map((item) => item.jurisdiction);
    const links = rawData.value.map(
      (item) =>
        `/search?jurisdiction=${encodeURIComponent(item.jurisdiction)}&type=Court+Decisions&sortBy=date`,
    );

    return {
      xValues,
      yValues,
      links,
    };
  });

  return {
    data,
    isLoading,
    error,
  };
}
