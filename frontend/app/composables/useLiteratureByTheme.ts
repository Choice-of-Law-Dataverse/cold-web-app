import { computed, type Ref } from "vue";
import { useSearch } from "@/composables/useSearch";
import type { SearchParams, SearchResponse } from "@/types/api";
import {
  type Literature,
  type LiteratureResponse,
  processLiterature,
} from "@/types/entities/literature";

export function useLiteratureByTheme(themes: Ref<string | undefined>) {
  const searchParams: Ref<SearchParams> = computed(() => ({
    query: "",
    filters: {
      theme: themes.value || "",
      type: "Literature",
    },
    pageSize: 100,
    enabledOverride: !!themes.value,
  }));

  const { data: searchResults, isLoading } = useSearch(searchParams);

  const data = computed<Literature[]>(() => {
    if (!searchResults.value?.pages) return [];
    return searchResults.value.pages
      .flatMap((page: SearchResponse) => page.results)
      .map((item) => processLiterature(item as LiteratureResponse));
  });

  return {
    data,
    isLoading,
  };
}
