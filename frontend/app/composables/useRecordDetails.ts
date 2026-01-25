import { computed, type ComputedRef, type Ref } from "vue";
import { useQuery, useQueries } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { TableName, TableResponseMap } from "@/types/api";
import { processDomesticInstrument } from "@/types/entities/domestic-instrument";
import { processInternationalInstrument } from "@/types/entities/international-instrument";
import { processRegionalInstrument } from "@/types/entities/regional-instrument";
import { processCourtDecision } from "@/types/entities/court-decision";
import { type Question, processQuestion } from "@/types/entities/question";
import { processLiterature } from "@/types/entities/literature";
import { processArbitralAward } from "@/types/entities/arbitral-award";
import { processArbitralRule } from "@/types/entities/arbitral-rule";

async function fetchRecordDetails<
  T extends TableName,
  TProcessed = TableResponseMap[T],
>(
  table: T,
  id: string | number,
  process?: (raw: TableResponseMap[T]) => TProcessed,
) {
  const { apiClient } = useApiClient();
  const raw = await apiClient<TableResponseMap[T]>("/search/details", {
    body: { table, id },
  });
  return process ? process(raw) : (raw as unknown as TProcessed);
}

export function useRecordDetails<
  T extends TableName,
  TProcessed = TableResponseMap[T],
>(
  table: T,
  id: Ref<string | number>,
  process?: (raw: TableResponseMap[T]) => TProcessed,
) {
  return useQuery({
    queryKey: computed(() => [table, id.value]),
    queryFn: () => fetchRecordDetails(table, id.value, process),
    enabled: computed(() => Boolean(id.value)),
  });
}

export function useRecordDetailsList<
  T extends TableName,
  TProcessed = TableResponseMap[T],
>(
  table: T,
  ids: Ref<Array<string | number>>,
  process?: (raw: TableResponseMap[T]) => TProcessed,
): {
  data: ComputedRef<(TProcessed | undefined)[]>;
  isLoading: ComputedRef<boolean>;
  hasError: ComputedRef<boolean>;
  error: ComputedRef<unknown>;
} {
  const queries = computed(() => {
    const list = ids.value || [];
    return list.map((id) => ({
      queryKey: [table, id],
      queryFn: () => fetchRecordDetails(table, id, process),
      enabled: Boolean(id),
    }));
  });

  const results = useQueries({ queries });

  const data: ComputedRef<(TProcessed | undefined)[]> = computed(() =>
    results.value.map((r) => r.data as TProcessed | undefined),
  );
  const isLoading = computed(() => results.value.some((r) => r.isLoading));
  const hasError = computed(() => results.value.some((r) => r.isError));
  const error = computed(() => results.value.find((r) => r.isError)?.error);

  return { data, isLoading, hasError, error };
}

// Entity-specific composables

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
  return useRecordDetails("Answers", id, processQuestion);
}

export function useLiterature(id: Ref<string | number>) {
  return useRecordDetails("Literature", id);
}

export function useArbitralAward(id: Ref<string | number>) {
  return useRecordDetails("Arbitral Awards", id, processArbitralAward);
}

export function useArbitralRule(id: Ref<string | number>) {
  return useRecordDetails("Arbitral Rules", id, processArbitralRule);
}

// List-based composables

export function useCourtDecisionsList(ids: Ref<(string | number)[]>) {
  return useRecordDetailsList("Court Decisions", ids, processCourtDecision);
}

export function useDomesticInstrumentsList(ids: Ref<(string | number)[]>) {
  return useRecordDetailsList(
    "Domestic Instruments",
    ids,
    processDomesticInstrument,
  );
}

export function useLiteratures(ids: Ref<string>) {
  const literatureIds = computed(() =>
    ids.value
      ? ids.value
          .split(",")
          .map((id: string) => id.trim())
          .filter((id: string) => id)
      : [],
  );

  return useRecordDetailsList("Literature", literatureIds, processLiterature);
}

export function useRelatedQuestions(
  jurisdictionCode: Ref<string>,
  questions: Ref<string>,
) {
  const questionList = computed(() =>
    questions.value
      ? questions.value
          .split(",")
          .map((q) => q.trim())
          .filter((q) => q)
      : [],
  );

  const compositeIds = computed(() =>
    jurisdictionCode.value && questionList.value.length
      ? questionList.value.map((qid) => `${jurisdictionCode.value}_${qid}`)
      : [],
  );

  const results = useRecordDetailsList(
    "Answers",
    compositeIds,
    processQuestion,
  );

  const items = computed(() => {
    const dataById = new Map<string, Question>();
    for (let i = 0; i < compositeIds.value.length; i++) {
      const record = results.data.value?.[i];
      const compositeId = compositeIds.value[i];
      if (record && compositeId) {
        dataById.set(compositeId, record);
      }
    }

    return questionList.value.map((qid) => {
      const id = `${jurisdictionCode.value}_${qid}`;
      const record = dataById.get(id);
      return {
        id,
        title: record?.Question || id,
      };
    });
  });

  return {
    items,
    isLoading: results.isLoading,
    hasError: results.hasError,
    error: results.error,
  };
}
