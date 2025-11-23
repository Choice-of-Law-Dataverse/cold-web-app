import { computed, type Ref } from "vue";
import { useSearch } from "~/composables/useSearch";
import type { SearchParams } from "@/types/api";

export function useCourtDecisionsByJurisdiction(jurisdiction: Ref<string>) {
  const searchParams = computed<SearchParams>(() => ({
    filters: {
      jurisdiction: jurisdiction.value || "",
      sortBy: "relevance",
      type: "Court Decisions",
    },
    pageSize: 100,
    query: "",
  }));

  const searchQuery = useSearch(searchParams);

  return {
    data: computed(() => {
      if (!searchQuery.data.value?.pages?.[0]) return [];
      return searchQuery.data.value.pages[0].results || [];
    }),
    isLoading: searchQuery.isLoading,
    error: searchQuery.error,
  };
}
