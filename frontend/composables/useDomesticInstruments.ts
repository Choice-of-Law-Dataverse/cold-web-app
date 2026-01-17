import { useApiClient } from "@/composables/useApiClient";
import { useQuery } from "@tanstack/vue-query";
import type { Ref } from "vue";
import type { FullTableRequest } from "@/types/api";
import type { DomesticInstrumentResponse } from "@/types/entities/domestic-instrument";

async function fetchDomesticInstruments(): Promise<
  DomesticInstrumentResponse[]
> {
  const { apiClient } = useApiClient();
  const body: FullTableRequest = {
    table: "Domestic Instruments",
  };

  const data = await apiClient<DomesticInstrumentResponse[]>(
    "/search/full_table",
    { body },
  );

  if (!Array.isArray(data)) {
    return [];
  }

  // Sort by date descending during fetch (cached)
  return data.sort((a, b) => Number(b.Date) - Number(a.Date));
}

export function useDomesticInstruments({
  filterCompatible,
}: {
  filterCompatible: Ref<boolean>;
}) {
  return useQuery({
    queryKey: ["domesticInstruments"],
    queryFn: fetchDomesticInstruments,
    select: (data) => {
      // Filtering happens on read (not cached) to avoid re-fetching on toggle
      if (filterCompatible.value) {
        return data.filter(
          (item) => item["Compatible With the HCCH Principles"] === true,
        );
      }
      return data;
    },
  });
}
