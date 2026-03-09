import { ref, computed, watch } from "vue";
import { useRecordDetails } from "./useRecordDetails";
import type {
  DomesticLegalProvision,
  RegionalLegalProvision,
} from "@/types/entities/legal-provision";
import {
  processDomesticLegalProvision,
  processRegionalLegalProvision,
} from "@/types/entities/legal-provision";

type LegalProvisionTable =
  | "Domestic Legal Provisions"
  | "Regional Legal Provisions";

function useDomesticProvision(idRef: Ref<string | number>) {
  return useRecordDetails(
    "Domestic Legal Provisions",
    idRef,
    processDomesticLegalProvision,
  );
}

function useRegionalProvision(idRef: Ref<string | number>) {
  return useRecordDetails(
    "Regional Legal Provisions",
    idRef,
    processRegionalLegalProvision,
  );
}

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
  const idRef = ref<string | number>(provisionId);

  const isRegional = table === "Regional Legal Provisions";

  const {
    data,
    isLoading: loading,
    error,
  } = isRegional ? useRegionalProvision(idRef) : useDomesticProvision(idRef);

  const title = computed(() => {
    if (!data.value) return "";
    if (isRegional) {
      return (data.value as RegionalLegalProvision).titleOfTheProvision || "";
    }
    return (data.value as DomesticLegalProvision).article || "";
  });

  const content = computed(() => {
    if (!data.value) return "";
    if (isRegional) {
      return (data.value as RegionalLegalProvision).fullText || "";
    }
    const domestic = data.value as DomesticLegalProvision;
    if (
      showEnglish.value &&
      domestic.fullTextOfTheProvisionEnglishTranslation
    ) {
      return domestic.fullTextOfTheProvisionEnglishTranslation;
    }
    return domestic.fullTextOfTheProvisionOriginalLanguage || "";
  });

  const hasEnglishTranslation = computed(() => {
    if (isRegional || !data.value) return false;
    return (data.value as DomesticLegalProvision).hasEnglishTranslation;
  });

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
