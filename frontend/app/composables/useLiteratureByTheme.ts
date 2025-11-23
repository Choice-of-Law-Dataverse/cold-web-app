import { computed, type Ref } from "vue";
import { useSearch } from "@/composables/useSearch";
import type { SearchParams, SearchResponse } from "@/types/api";

interface LiteratureItem {
  id: string;
  Title?: string;
  title?: string;
  "OUP JD Chapter"?: boolean;
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

  const literatureFromThemes = computed(() => {
    if (!searchResults.value?.pages) return [];
    return searchResults.value.pages
      .flatMap((page: SearchResponse) => page.results)
      .map((item) => {
        const litItem = item as unknown as LiteratureItem;
        return {
          id: litItem.id,
          title: litItem.Title || litItem.title || "Untitled",
          "OUP JD Chapter": litItem["OUP JD Chapter"],
        };
      });
  });

  return {
    data: literatureFromThemes,
    isLoading,
  };
}
