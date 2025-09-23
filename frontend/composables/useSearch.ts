import { computed, type Ref } from "vue";
import { useInfiniteQuery } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type {
  EnhancedSearchRequest,
  SearchParams,
  SearchResponse,
} from "~/types/api";

const fetchSearchResults = async ({
  query,
  filters,
  page = 1,
  pageSize = 10,
}: SearchParams): Promise<SearchResponse> => {
  const { apiClient } = useApiClient();

  const body: EnhancedSearchRequest = {
    search_string: query || "",
    page,
    page_size: pageSize,
    filters: [],
  };

  // Add sort_by_date if needed
  if (filters.sortBy === "date") {
    body.sort_by_date = true;
  } else {
    body.sort_by_date = false;
  }

  // Add "Jurisdictions" filter if defined
  if (filters.jurisdiction) {
    body.filters.push({
      column: "jurisdictions",
      values: filters.jurisdiction.split(","),
    });
  }

  // Add "Themes" filter if defined
  if (filters.theme) {
    body.filters.push({
      column: "themes",
      values: filters.theme.split(","),
    });
  }

  // Set up mapping: Filter options have different wording to table names
  const typeFilterMapping: Record<string, string> = {
    Questions: "Answers",
    "Court Decisions": "Court Decisions",
    "Legal Instruments": "Domestic Instruments",
    "Domestic Instruments": "Domestic Instruments",
    "Regional Instruments": "Regional Instruments",
    "International Instruments": "International Instruments",
    Literature: "Literature",
  };

  // Add "Type" filter if defined
  if (filters.type) {
    body.filters.push({
      column: "tables",
      values: filters.type
        .split(",")
        .map((type) => typeFilterMapping[type] || type),
    });
  }

  const data = await apiClient<{
    results: Record<string, unknown>[];
    total_matches?: number;
  }>("/search/", { body });

  return {
    results: Object.values(data.results),
    totalMatches: data.total_matches || 0,
  };
};

export function useSearch(searchParams: Ref<SearchParams>) {
  return useInfiniteQuery({
    queryKey: computed(() => ["search", searchParams.value]),
    queryFn: ({ pageParam }) =>
      fetchSearchResults({ ...searchParams.value, page: pageParam }),
    initialPageParam: 1,
    enabled: computed(() => {
      const params = searchParams.value;
      if (typeof params.enabledOverride !== "undefined") {
        return !!params.enabledOverride;
      }
      return !!(
        params.query ||
        params.filters.jurisdiction ||
        params.filters.theme ||
        params.filters.type
      );
    }),
    getNextPageParam: (lastPage, allPages, lastPageParam) => {
      const totalItems = lastPage.totalMatches;
      const pageSize = searchParams.value.pageSize || 10;
      const totalPages = Math.ceil(totalItems / pageSize);
      const currentPage = lastPageParam;

      return currentPage < totalPages ? currentPage + 1 : undefined;
    },
  });
}
