import { computed, type Ref } from "vue";
import { useSearch } from "~/composables/useSearch";
import type { SearchParams } from "@/types/api";
import type { RelatedItem } from "@/types/ui";

interface DomesticInstrumentSearchResult {
  id?: string;
  "Title (in English)"?: string;
  Abbreviation?: string;
}

function isValidTitle(title: string | undefined): boolean {
  if (!title) return false;
  return title !== "Untitled" && title !== "NA";
}

function processToRelatedItems(
  results: DomesticInstrumentSearchResult[],
): RelatedItem[] {
  const items: RelatedItem[] = [];
  for (const item of results) {
    if (!item.id) continue;
    const title = item["Title (in English)"] || item.Abbreviation;
    if (!isValidTitle(title)) continue;
    items.push({ id: item.id, title: title! });
  }
  return items;
}

export function useDomesticInstrumentsByJurisdiction(
  jurisdiction: Ref<string>,
) {
  const searchParams = computed<SearchParams>(() => ({
    filters: {
      jurisdiction: jurisdiction.value || "",
      sortBy: "relevance",
      type: "Domestic Instruments",
    },
    pageSize: 100,
    query: "",
  }));

  const searchQuery = useSearch(searchParams);

  return {
    data: computed(() => {
      const results = searchQuery.data.value?.pages?.[0]?.results || [];
      return processToRelatedItems(results as DomesticInstrumentSearchResult[]);
    }),
    isLoading: searchQuery.isLoading,
    error: searchQuery.error,
  };
}
