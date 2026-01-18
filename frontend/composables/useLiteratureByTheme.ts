import { computed, type Ref } from "vue";
import { useSearch } from "@/composables/useSearch";
import type { SearchParams, SearchResponse } from "@/types/api";
import type { Literature } from "@/types/entities/literature";

interface LiteratureSearchResult {
  id: string;
  Title?: string;
  title?: string;
  "OUP JD Chapter"?: boolean;
}

function processToLiterature(item: LiteratureSearchResult): Literature {
  const displayTitle = item.Title || item.title || "Untitled";
  return {
    id: item.id,
    Title: item.Title,
    displayTitle,
    isOupChapter: Boolean(item["OUP JD Chapter"]),
  } as Literature;
}

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
      .map((item) =>
        processToLiterature(item as unknown as LiteratureSearchResult),
      );
  });

  return {
    data,
    isLoading,
  };
}
