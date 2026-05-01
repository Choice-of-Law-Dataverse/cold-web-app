import { computed, type Ref } from "vue";
import { useFullTableWithFilters } from "@/composables/useFullTable";
import type { TypedFilter } from "@/types/api";
import type { DomesticInstrumentResponse } from "@/types/entities/domestic-instrument";

export function useDomesticInstruments({
  filterCompatible,
  limit,
}: {
  filterCompatible: Ref<boolean>;
  limit?: number;
}) {
  const filters = computed<TypedFilter<"Domestic Instruments">[]>(() =>
    filterCompatible.value
      ? [{ column: "compatibleWithTheHcchPrinciples", value: true }]
      : [],
  );

  return useFullTableWithFilters<
    "Domestic Instruments",
    DomesticInstrumentResponse
  >("Domestic Instruments", filters, {
    limit,
    orderBy: limit ? "date" : undefined,
    orderDir: limit ? "desc" : undefined,
    select: (data) =>
      data.slice().sort((a, b) => Number(b.date) - Number(a.date)),
  });
}
