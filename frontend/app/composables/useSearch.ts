import { computed, type Ref } from "vue";
import { useInfiniteQuery } from "@tanstack/vue-query";
import type createClient from "openapi-fetch";
import { useApiClient } from "@/composables/useApiClient";
import type { SearchParams, SearchResponse } from "@/types/api";
import type { paths } from "@/types/api-schema";

const TYPE_FILTER_MAPPING: Record<string, string> = {
  Questions: "Answers",
  "Court Decisions": "Court Decisions",
  "Legal Instruments": "Domestic Instruments",
  "Domestic Instruments": "Domestic Instruments",
  "Regional Instruments": "Regional Instruments",
  "International Instruments": "International Instruments",
  Literature: "Literature",
  "Arbitral Awards": "Arbitral Awards",
  "Arbitral Rules": "Arbitral Rules",
};

const splitCsv = (value: string | undefined): string[] | undefined =>
  value ? value.split(",").filter(Boolean) : undefined;

const fetchSearchResults = async (
  client: ReturnType<typeof createClient<paths>>,
  { query, filters, page = 1, pageSize = 10 }: SearchParams,
): Promise<SearchResponse> => {
  const types = splitCsv(filters.type)?.map(
    (type) => TYPE_FILTER_MAPPING[type] || type,
  );

  const { data, error } = await client.GET("/search/", {
    params: {
      query: {
        search_string: query || "",
        page,
        page_size: pageSize,
        sort_by_date: filters.sortBy === "date",
        jurisdictions: splitCsv(filters.jurisdiction),
        themes: splitCsv(filters.theme),
        tables: types,
      },
    },
  });

  if (error) throw error;

  return {
    results: data.results,
    totalMatches: data.totalMatches || 0,
  };
};

export function useSearch(searchParams: Ref<SearchParams>) {
  const { client } = useApiClient();

  return useInfiniteQuery({
    queryKey: computed(() => ["search", searchParams.value]),
    queryFn: ({ pageParam }) =>
      fetchSearchResults(client, {
        ...searchParams.value,
        page: pageParam,
      }),
    initialPageParam: 1,
    enabled: computed(() => {
      const params = searchParams.value;
      if (typeof params.enabledOverride !== "undefined") {
        return !!params.enabledOverride;
      }
      return !!(
        (params.query && params.query.trim()) ||
        params.filters.jurisdiction ||
        params.filters.theme ||
        params.filters.type
      );
    }),
    getNextPageParam: (lastPage, _allPages, lastPageParam) => {
      const totalItems = lastPage.totalMatches;
      const pageSize = searchParams.value.pageSize || 10;
      const totalPages = Math.ceil(totalItems / pageSize);
      const currentPage = lastPageParam;

      return currentPage < totalPages ? currentPage + 1 : undefined;
    },
  });
}
