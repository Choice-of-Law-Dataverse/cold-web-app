import { ref, computed, watch } from "vue";
import { useRecordDetails } from "./useRecordDetails";
import type { TableName } from "@/types/api";
import {
  type LegalProvision,
  type DomesticLegalProvisionResponse,
  type RegionalLegalProvisionResponse,
  processDomesticLegalProvision,
  processRegionalLegalProvision,
} from "@/types/entities/legal-provision";

type LegalProvisionTable =
  | "Domestic Legal Provisions"
  | "Regional Legal Provisions";

export function useLegalProvision({
  provisionId,
  onHasEnglishTranslationUpdate,
  table = "Domestic Legal Provisions",
}: {
  provisionId: string;
  onHasEnglishTranslationUpdate?: (hasTranslation: boolean) => void;
  table?: LegalProvisionTable;
}) {
  const showEnglish = ref(true);
  const tableRef = ref<TableName>(table);
  const idRef = ref<string | number>(provisionId);

  const isRegional = table === "Regional Legal Provisions";

  const {
    data,
    isLoading: loading,
    error,
  } = isRegional
    ? useRecordDetails<RegionalLegalProvisionResponse, LegalProvision>(
        tableRef,
        idRef,
        processRegionalLegalProvision,
      )
    : useRecordDetails<DomesticLegalProvisionResponse, LegalProvision>(
        tableRef,
        idRef,
        processDomesticLegalProvision,
      );

  const title = computed(() => data.value?.title || "");

  const content = computed(() => {
    if (!data.value) return "";
    if (showEnglish.value && data.value.englishText) {
      return data.value.englishText;
    }
    return data.value.originalText;
  });

  const hasEnglishTranslation = computed(
    () => data.value?.hasEnglishTranslation || false,
  );

  const anchorId = computed(() => {
    const articleNumber = title.value
      ? title.value.replace(/\s+/g, "")
      : provisionId.replace(/\s+/g, "");
    return articleNumber;
  });

  watch(
    hasEnglishTranslation,
    (value) => {
      onHasEnglishTranslationUpdate?.(value);
    },
    { immediate: true },
  );

  return {
    data,
    title,
    content,
    loading,
    error,
    hasEnglishTranslation,
    showEnglish,
    anchorId,
  };
}
