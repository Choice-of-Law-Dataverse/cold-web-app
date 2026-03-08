import { computed, type Ref } from "vue";
import { useInfiniteQuery } from "@tanstack/vue-query";
import type createClient from "openapi-fetch";
import { useApiClient } from "@/composables/useApiClient";
import type { SearchParams, SearchResponse } from "@/types/api";
import type { paths } from "@/types/api-schema";

const fetchSearchResults = async (
  client: ReturnType<typeof createClient<paths>>,
  { query, filters, page = 1, pageSize = 10 }: SearchParams,
): Promise<SearchResponse> => {
  const searchFilters: { column: string; values: string[] }[] = [];

  if (filters.jurisdiction) {
    searchFilters.push({
      column: "jurisdictions",
      values: filters.jurisdiction.split(","),
    });
  }

  if (filters.theme) {
    searchFilters.push({
      column: "themes",
      values: filters.theme.split(","),
    });
  }

  const typeFilterMapping: Record<string, string> = {
    Questions: "Answers",
    "Court Decisions": "Court Decisions",
    "Legal Instruments": "Domestic Instruments",
    "Domestic Instruments": "Domestic Instruments",
    "Regional Instruments": "Regional Instruments",
    "International Instruments": "International Instruments",
    Literature: "Literature",
  };

  if (filters.type) {
    searchFilters.push({
      column: "tables",
      values: filters.type
        .split(",")
        .map((type) => typeFilterMapping[type] || type),
    });
  }

  const { data, error } = await client.POST("/search/", {
    body: {
      search_string: query || "",
      page,
      page_size: pageSize,
      filters: searchFilters,
      sort_by_date: filters.sortBy === "date",
      response_type: null,
    },
  });

  if (error) throw error;

  return {
    results: data.results as Record<string, unknown>[],
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
