import { computed, type Ref } from "vue";
import { useQuery } from "@tanstack/vue-query";
import type createClient from "openapi-fetch";
import { useApiClient } from "@/composables/useApiClient";
import type { TableName, TableDetailMap } from "@/types/api";
import type { paths } from "@/types/api-schema";
import { processDomesticInstrument } from "@/types/entities/domestic-instrument";
import { processInternationalInstrument } from "@/types/entities/international-instrument";
import { processRegionalInstrument } from "@/types/entities/regional-instrument";
import { processCourtDecision } from "@/types/entities/court-decision";
import { processQuestion } from "@/types/entities/question";
import { processLiterature } from "@/types/entities/literature";
import { processArbitralAward } from "@/types/entities/arbitral-award";
import { processArbitralRule } from "@/types/entities/arbitral-rule";
import { processJurisdiction } from "@/types/entities/jurisdiction";
import { processSpecialist } from "@/types/entities/specialist";

type ApiClient = ReturnType<typeof createClient<paths>>;

async function fetchRecordDetails<
  T extends TableName,
  TProcessed = TableDetailMap[T],
>(
  client: ApiClient,
  table: T,
  id: string | number,
  process?: (raw: TableDetailMap[T]) => TProcessed,
) {
  const { data, error } = await client.POST("/search/details", {
    body: { table, id: String(id) },
  });
  if (error) throw error;
  const raw = data as unknown as TableDetailMap[T];
  return process ? process(raw) : (raw as unknown as TProcessed);
}

export function useRecordDetails<
  T extends TableName,
  TProcessed = TableDetailMap[T],
>(
  table: T,
  id: Ref<string | number>,
  process?: (raw: TableDetailMap[T]) => TProcessed,
) {
  const { client } = useApiClient();

  return useQuery({
    queryKey: computed(() => [table, id.value]),
    queryFn: () => fetchRecordDetails(client, table, id.value, process),
    enabled: computed(() => Boolean(id.value)),
  });
}

export function useDomesticInstrument(id: Ref<string | number>) {
  return useRecordDetails(
    "Domestic Instruments",
    id,
    processDomesticInstrument,
  );
}

export function useInternationalInstrument(id: Ref<string | number>) {
  return useRecordDetails(
    "International Instruments",
    id,
    processInternationalInstrument,
  );
}

export function useRegionalInstrument(id: Ref<string | number>) {
  return useRecordDetails(
    "Regional Instruments",
    id,
    processRegionalInstrument,
  );
}

export function useCourtDecision(id: Ref<string | number>) {
  return useRecordDetails("Court Decisions", id, processCourtDecision);
}

export function useAnswer(id: Ref<string | number>) {
  const { client } = useApiClient();
  const table = computed(() =>
    String(id.value).includes("_") ? "Answers" : "Questions",
  );

  return useQuery({
    queryKey: computed(() => [table.value, id.value]),
    queryFn: async () => {
      const { data, error } = await client.POST("/search/details", {
        body: { table: table.value, id: String(id.value) },
      });
      if (error) throw error;
      return processQuestion(data as Parameters<typeof processQuestion>[0]);
    },
    enabled: computed(() => Boolean(id.value)),
  });
}

export function useLiterature(id: Ref<string | number>) {
  return useRecordDetails("Literature", id, processLiterature);
}

export function useArbitralAward(id: Ref<string | number>) {
  return useRecordDetails("Arbitral Awards", id, processArbitralAward);
}

export function useArbitralRule(id: Ref<string | number>) {
  return useRecordDetails("Arbitral Rules", id, processArbitralRule);
}

export function useJurisdictionDetail(id: Ref<string | number>) {
  return useRecordDetails("Jurisdictions", id, processJurisdiction);
}

export function useSpecialistDetail(id: Ref<string | number>) {
  return useRecordDetails("Specialists", id, processSpecialist);
}
