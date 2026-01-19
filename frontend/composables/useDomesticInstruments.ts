import type { Ref } from "vue";
import { useFullTable } from "@/composables/useFullTable";
import type { DomesticInstrumentResponse } from "@/types/entities/domestic-instrument";

export function useDomesticInstruments({
  filterCompatible,
}: {
  filterCompatible: Ref<boolean>;
}) {
  return useFullTable<"Domestic Instruments", DomesticInstrumentResponse>(
    "Domestic Instruments",
    {
      select: (data) => {
        // Sort by date descending
        const sorted = data
          .slice()
          .sort((a, b) => Number(b.Date) - Number(a.Date));
        // Filter by compatibility if enabled
        if (filterCompatible.value) {
          return sorted.filter(
            (item) => item["Compatible With the HCCH Principles"] === true,
          );
        }
        return sorted;
      },
    },
  );
}
