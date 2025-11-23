import { computed, type Ref } from "vue";
import { useSearch } from "~/composables/useSearch";
import type { SearchParams } from "@/types/api";

export const useCourtDecisionsCount = (
  jurisdictionId: Ref<string | undefined>,
) => {
  const searchParams = computed<SearchParams>(() => ({
    filters: {
      jurisdiction: jurisdictionId.value || "",
      sortBy: "relevance",
      type: "Court Decisions",
    },
    pageSize: 10,
    query: "",
  }));

  const searchQuery = useSearch(searchParams);

  return {
    data: computed(() => {
      if (!searchQuery.data.value?.pages?.[0]) return undefined;
      return searchQuery.data.value.pages[0].totalMatches;
    }),
    isLoading: searchQuery.isLoading,
    error: searchQuery.error,
  };
};

export const useDomesticInstrumentsCount = (
  jurisdictionId: Ref<string | undefined>,
) => {
  const searchParams = computed<SearchParams>(() => ({
    filters: {
      jurisdiction: jurisdictionId.value || "",
      sortBy: "relevance",
      type: "Domestic Instruments",
    },
    pageSize: 10,
    query: "",
  }));

  const searchQuery = useSearch(searchParams);

  return {
    data: computed(() => {
      if (!searchQuery.data.value?.pages?.[0]) return undefined;
      return searchQuery.data.value.pages[0].totalMatches;
    }),
    isLoading: searchQuery.isLoading,
    error: searchQuery.error,
  };
};
