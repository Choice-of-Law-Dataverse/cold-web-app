import { computed, ref } from "vue";
import { useCountByJurisdiction } from "@/composables/useCountByJurisdiction";

export function useJurisdictionChart() {
  const tableName = ref("Court_Decisions");
  const { data: rawData, isLoading, error } = useCountByJurisdiction(tableName);

  const data = computed(() => {
    if (!rawData.value) return null;

    const xValues = rawData.value.map((item) => item.n);
    const yValues = rawData.value.map((item) => item.jurisdiction);
    const links = rawData.value.map(
      (item) =>
        `/search?jurisdiction=${encodeURIComponent(item.jurisdiction)}&type=Court+Decisions`,
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
