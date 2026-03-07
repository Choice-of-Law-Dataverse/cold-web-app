import { computed, type Ref } from "vue";
import { useSearch } from "~/composables/useSearch";
import type { SearchParams } from "@/types/api";
import type { RelatedItem } from "@/types/ui";

interface CourtDecisionSearchResult {
  id?: string;
  caseTitle?: string;
  caseCitation?: string;
}

function isValidTitle(title: string | undefined): boolean {
  if (!title) return false;
  return title !== "Untitled" && title !== "NA";
}

function processToRelatedItems(
  results: CourtDecisionSearchResult[],
): RelatedItem[] {
  const items: RelatedItem[] = [];
  for (const item of results) {
    if (!item.id) continue;
    const title = item.caseTitle || item.caseCitation;
    if (!isValidTitle(title)) continue;
    items.push({ id: item.id, title: title! });
  }
  return items;
}

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
      const results = searchQuery.data.value?.pages?.[0]?.results || [];
      return processToRelatedItems(results as CourtDecisionSearchResult[]);
    }),
    isLoading: searchQuery.isLoading,
    error: searchQuery.error,
  };
}
