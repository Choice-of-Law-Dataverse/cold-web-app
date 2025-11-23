import { computed, type Ref } from "vue";
import { useQueries } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { FullTableRequest } from "@/types/api";

const fetchQuestionLabel = async (id: string | number) => {
  const { apiClient } = useApiClient();
  const body: FullTableRequest = {
    table: "Questions",
    filters: [{ column: "ID", value: id }],
  };
  const data = await apiClient("/search/full_table", { body });
  return Array.isArray(data) && data[0]?.Question
    ? data[0].Question
    : String(id);
};

export function useQuestionLabelsByIds(
  ids: Ref<Array<string | number>>,
  enabled: Ref<boolean> | boolean = true,
) {
  const queries = computed(() => {
    return (ids.value || []).map((id) => ({
      queryKey: ["questionLabel", id],
      queryFn: () => fetchQuestionLabel(id),
      enabled: Boolean(
        (typeof enabled === "object" ? enabled.value : enabled) && id,
      ),
    }));
  });

  const results = useQueries({ queries });

  const labels = computed<string[]>(() => {
    return (ids.value || []).map((id, idx) => {
      const res = results.value[idx];
      return (res?.data as string) || String(id);
    });
  });

  const isLoading = computed(() => results.value.some((r) => r.isLoading));
  const hasError = computed(() => results.value.some((r) => r.isError));

  return { labels, isLoading, hasError, results };
}
