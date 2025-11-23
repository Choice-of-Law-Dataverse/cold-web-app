import { computed, ref } from "vue";
import { useCountByJurisdiction } from "@/composables/useCountByJurisdiction";
import type { TableName } from "@/types/api";

export function useJurisdictionChart() {
  const tableName = ref("Court Decisions" as TableName);
  const limit = ref(6);
  const {
    data: rawData,
    isLoading,
    error,
  } = useCountByJurisdiction(tableName, limit);

  const data = computed(() => {
    if (!rawData.value) return null;

    const xValues = rawData.value.map((item) => item.n);
    const yValues = rawData.value.map((item) => item.jurisdiction);
    const links = rawData.value.map(
      (item) =>
        `/search?jurisdiction=${encodeURIComponent(item.jurisdiction)}&type=Court+Decisions&sortBy=date`,
    );

    return {
      xValues,
      yValues,
      links,
    };
  });

  return {
    data,
    isLoading,
    error,
  };
}
