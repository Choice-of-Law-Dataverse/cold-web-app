import { computed, ref, type Ref, type MaybeRefOrGetter } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type {
  JurisdictionWithAnswerCoverage,
  JurisdictionCount,
  TableName,
} from "@/types/api";

const EMPTY_SET = new Set<string>();
const EMPTY_MAP = new Map<string, ProcessedJurisdiction>();

export interface ProcessedJurisdiction extends JurisdictionWithAnswerCoverage {
  label: string;
  alpha3Code: string | undefined;
  avatar: string | undefined;
  answerCoverage: number | undefined;
}

interface JurisdictionsData {
  jurisdictions: ProcessedJurisdiction[];
  knownJurisdictionTerms: Set<string>;
  /** Map from lowercase name to jurisdiction */
  byName: Map<string, ProcessedJurisdiction>;
  /** Map from lowercase alpha-3 code to jurisdiction */
  byAlpha3: Map<string, ProcessedJurisdiction>;
  /** Set of lowercase alpha-3 codes for jurisdictions with coverage > 0 */
  coveredCountries: Set<string>;
}

function processJurisdiction(
  record: JurisdictionWithAnswerCoverage,
): ProcessedJurisdiction {
  return {
    ...record,
    Name: record?.Name || "N/A",
    "Jurisdiction Summary": record?.["Jurisdiction Summary"] || "N/A",
    "Jurisdictional Differentiator":
      record?.["Jurisdictional Differentiator"] || "N/A",
    "Legal Family": record?.["Legal Family"] || "N/A",
    Specialists: record?.Specialists || "",
    Literature: record?.Literature,
    label: record.Name as string,
    alpha3Code: record["Alpha-3 Code"] as string | undefined,
    avatar: record["Alpha-3 Code"]
      ? `https://choiceoflaw.blob.core.windows.net/assets/flags/${String(
          record["Alpha-3 Code"],
        ).toLowerCase()}.svg`
      : undefined,
    answerCoverage: record["Answer Coverage"],
  };
}

async function fetchAndProcessJurisdictions(): Promise<JurisdictionsData> {
  const { apiClient } = useApiClient();

  const rawData = await apiClient<JurisdictionWithAnswerCoverage[]>(
    "/statistics/jurisdictions-with-answer-percentage",
    { method: "GET" },
  );

  const jurisdictions = rawData
    .filter((record) => record["Irrelevant?"] === false)
    .map(processJurisdiction);

  const knownJurisdictionTerms = new Set<string>();
  const byName = new Map<string, ProcessedJurisdiction>();
  const byAlpha3 = new Map<string, ProcessedJurisdiction>();
  const coveredCountries = new Set<string>();

  for (const j of jurisdictions) {
    const nameLower = j.Name.toLowerCase();
    knownJurisdictionTerms.add(nameLower);
    byName.set(nameLower, j);

    if (j.alpha3Code) {
      const codeLower = j.alpha3Code.toLowerCase();
      knownJurisdictionTerms.add(codeLower);
      byAlpha3.set(codeLower, j);

      if (j.answerCoverage && j.answerCoverage > 0) {
        coveredCountries.add(codeLower);
      }
    }
  }

  return {
    jurisdictions,
    knownJurisdictionTerms,
    byName,
    byAlpha3,
    coveredCountries,
  };
}

export function useJurisdictions(enabled?: MaybeRefOrGetter<boolean>) {
  const { data, ...rest } = useQuery({
    queryKey: ["jurisdictions-with-answer-percentage"],
    queryFn: fetchAndProcessJurisdictions,
    enabled,
  });

  return {
    data: computed(() => data.value?.jurisdictions),
    knownJurisdictionTerms: computed(
      () => data.value?.knownJurisdictionTerms ?? EMPTY_SET,
    ),
    byName: computed(() => data.value?.byName ?? EMPTY_MAP),
    byAlpha3: computed(() => data.value?.byAlpha3 ?? EMPTY_MAP),
    coveredCountries: computed(() => data.value?.coveredCountries ?? EMPTY_SET),
    ...rest,
  };
}

export function useJurisdiction(iso3: Ref<string>) {
  const { byAlpha3, isLoading, error, isError, isFetching } =
    useJurisdictions();

  const data = computed(() => {
    if (!iso3.value) return undefined;
    return byAlpha3.value.get(iso3.value.toLowerCase());
  });

  return {
    data,
    isLoading,
    error,
    isError,
    isFetching,
  };
}

/**
 * Provides lookup utilities for jurisdictions using the API data.
 * Leverages TanStack Query cache from useJurisdictions for efficient data access.
 */
export function useJurisdictionLookup(enabled?: MaybeRefOrGetter<boolean>) {
  const {
    data: jurisdictions,
    knownJurisdictionTerms,
    byName,
    byAlpha3,
    ...rest
  } = useJurisdictions(enabled);

  /**
   * Finds the ISO-3 code for a given jurisdiction name. O(1) lookup.
   */
  const getJurisdictionISO = (name: string): string => {
    if (!name) return "default";
    const jurisdiction = byName.value.get(name.toLowerCase());
    return jurisdiction?.alpha3Code?.toLowerCase() || "default";
  };

  /**
   * Finds jurisdictions that match the given search words.
   * Note: This still requires iteration since it does partial matching.
   */
  const findMatchingJurisdictions = (words: string[]): string[] => {
    if (!jurisdictions.value || words.length === 0) return [];

    return jurisdictions.value
      .filter((j) =>
        words.some((word) => {
          const nameLower = j.Name.toLowerCase();
          const codeLower = j.alpha3Code?.toLowerCase() || "";
          return nameLower.includes(word) || codeLower.includes(word);
        }),
      )
      .map((j) => j.Name);
  };

  /**
   * Finds a jurisdiction by its exact name. O(1) lookup.
   */
  const findJurisdictionByName = (name: string) => {
    if (!name) return undefined;
    return byName.value.get(name.toLowerCase());
  };

  /**
   * Finds a jurisdiction by its alpha-3 code. O(1) lookup.
   */
  const findJurisdictionByCode = (code: string) => {
    if (!code) return undefined;
    return byAlpha3.value.get(code.toLowerCase());
  };

  /**
   * Checks if a word matches any jurisdiction term. O(1) lookup.
   */
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

/**
 * Returns a Set of lowercase alpha-3 codes for jurisdictions with answer coverage > 0.
 */
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

// --- Count by jurisdiction (different endpoint) ---

async function fetchCountByJurisdiction(tableName: TableName, limit?: number) {
  const { apiClient } = useApiClient();
  const params = new URLSearchParams({ table: tableName });
  if (limit) {
    params.append("limit", limit.toString());
  }
  return await apiClient<JurisdictionCount[]>(
    `/statistics/count-by-jurisdiction?${params.toString()}`,
    { method: "GET" },
  );
}

function useCountByJurisdiction(
  tableName: Ref<TableName>,
  limit?: Ref<number | undefined>,
) {
  return useQuery({
    queryKey: computed(() => [
      "countByJurisdiction",
      tableName.value,
      limit?.value,
    ]),
    queryFn: () => fetchCountByJurisdiction(tableName.value, limit?.value),
    enabled: computed(() => Boolean(tableName.value)),
  });
}

/**
 * Returns chart data for court decisions by jurisdiction.
 */
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
