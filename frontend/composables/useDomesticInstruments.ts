import { useApiClient } from "@/composables/useApiClient";
import { useQuery } from "@tanstack/vue-query";
import { computed, type Ref } from "vue";
import type { FullTableRequest } from "~/types/api";

const fetchDomesticInstrumentsData = async (_filterCompatible: boolean) => {
  const { apiClient } = useApiClient();
  const body: FullTableRequest = {
    table: "Domestic Instruments",
  };

  const data = await apiClient("/search/full_table", {
    body,
  });

  if (!Array.isArray(data)) {
    return [];
  }

  const instrumentsData = data as Record<string, unknown>[];
  instrumentsData.sort(
    (a: Record<string, unknown>, b: Record<string, unknown>) =>
      Number(b.Date) - Number(a.Date),
  );
  return instrumentsData;
};

export function useDomesticInstruments({
  filterCompatible,
}: {
  filterCompatible: Ref<boolean>;
}) {
  return useQuery({
    queryKey: computed(() =>
      filterCompatible.value
        ? ["domesticInstruments", "compatible"]
        : ["domesticInstruments"],
    ),
    queryFn: () => fetchDomesticInstrumentsData(filterCompatible.value),
    select: filterCompatible.value
      ? (data: Record<string, unknown>[]) =>
          data.filter(
            (item: Record<string, unknown>) =>
              item["Compatible With the HCCH Principles?"],
          )
      : undefined,
  });
}
