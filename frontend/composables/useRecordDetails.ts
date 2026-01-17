import { computed, type ComputedRef, type Ref } from "vue";
import { useQuery, useQueries } from "@tanstack/vue-query";
import { useApiClient } from "@/composables/useApiClient";
import type { TableName } from "@/types/api";
import {
  type DomesticInstrumentResponse,
  type DomesticInstrument,
  processDomesticInstrument,
} from "@/types/entities/domestic-instrument";
import {
  type InternationalInstrumentResponse,
  type InternationalInstrument,
  processInternationalInstrument,
} from "@/types/entities/international-instrument";
import {
  type RegionalInstrumentResponse,
  type RegionalInstrument,
  processRegionalInstrument,
} from "@/types/entities/regional-instrument";
import {
  type CourtDecisionResponse,
  type CourtDecision,
  processCourtDecision,
} from "@/types/entities/court-decision";
import {
  type QuestionResponse,
  type Question,
  processQuestion,
} from "@/types/entities/question";
import type { LiteratureResponse } from "@/types/entities/literature";
import {
  type ArbitralAwardResponse,
  type ArbitralAward,
  processArbitralAward,
} from "@/types/entities/arbitral-award";
import {
  type ArbitralRuleResponse,
  type ArbitralRule,
  processArbitralRule,
} from "@/types/entities/arbitral-rule";

async function fetchRecordDetails<TRaw, TProcessed = TRaw>(
  table: TableName,
  id: string | number,
  process?: (raw: TRaw) => TProcessed,
) {
  const { apiClient } = useApiClient();
  const raw = await apiClient<TRaw>("/search/details", { body: { table, id } });
  return process ? process(raw) : (raw as unknown as TProcessed);
}

export function useRecordDetails<TRaw, TProcessed = TRaw>(
  table: TableName,
  id: Ref<string | number>,
  process?: (raw: TRaw) => TProcessed,
) {
  return useQuery({
    queryKey: computed(() => [table, id.value]),
    queryFn: () =>
      fetchRecordDetails<TRaw, TProcessed>(table, id.value, process),
    enabled: computed(() => Boolean(id.value)),
  });
}

export function useRecordDetailsList<TRaw, TProcessed = TRaw>(
  table: TableName,
  ids: Ref<Array<string | number>>,
  process?: (raw: TRaw) => TProcessed,
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
      queryFn: () => fetchRecordDetails<TRaw, TProcessed>(table, id, process),
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
  return useRecordDetails<DomesticInstrumentResponse, DomesticInstrument>(
    "Domestic Instruments",
    id,
    processDomesticInstrument,
  );
}

export function useInternationalInstrument(id: Ref<string | number>) {
  return useRecordDetails<
    InternationalInstrumentResponse,
    InternationalInstrument
  >("International Instruments", id, processInternationalInstrument);
}

export function useRegionalInstrument(id: Ref<string | number>) {
  return useRecordDetails<RegionalInstrumentResponse, RegionalInstrument>(
    "Regional Instruments",
    id,
    processRegionalInstrument,
  );
}

export function useCourtDecision(id: Ref<string | number>) {
  return useRecordDetails<CourtDecisionResponse, CourtDecision>(
    "Court Decisions",
    id,
    processCourtDecision,
  );
}

export function useAnswer(id: Ref<string | number>) {
  return useRecordDetails<QuestionResponse, Question>(
    "Answers",
    id,
    processQuestion,
  );
}

export function useLiterature(id: Ref<string | number>) {
  return useRecordDetails<LiteratureResponse>("Literature", id);
}

export function useArbitralAward(id: Ref<string | number>) {
  return useRecordDetails<ArbitralAwardResponse, ArbitralAward>(
    "Arbitral Awards",
    id,
    processArbitralAward,
  );
}

export function useArbitralRule(id: Ref<string | number>) {
  return useRecordDetails<ArbitralRuleResponse, ArbitralRule>(
    "Arbitral Rules",
    id,
    processArbitralRule,
  );
}

// List-based composables

export function useLiteratures(ids: Ref<string>) {
  const literatureIds = computed(() =>
    ids.value
      ? ids.value
          .split(",")
          .map((id: string) => id.trim())
          .filter((id: string) => id)
      : [],
  );

  return useRecordDetailsList<LiteratureResponse>("Literature", literatureIds);
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

  const results = useRecordDetailsList<QuestionResponse, Question>(
    "Answers",
    compositeIds,
    processQuestion,
  );

  const questionLabels = computed(() => {
    const dataMap = compositeIds.value.reduce(
      (acc, id, index) => {
        const record = results.data.value?.[index];
        if (record) {
          acc[id] = record;
        }
        return acc;
      },
      {} as Record<string, Question>,
    );

    return questionList.value.map((qid) => {
      const id = `${jurisdictionCode.value}_${qid}`;
      const rec = dataMap[id];
      return rec?.Question || id;
    });
  });

  return {
    questionList,
    questionLabels,
    ...results,
  };
}
