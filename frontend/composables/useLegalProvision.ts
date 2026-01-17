import { ref, computed, watch } from "vue";
import { useRecordDetails } from "./useRecordDetails";
import type { TableName } from "@/types/api";

export function useLegalProvision({
  provisionId,
  onHasEnglishTranslationUpdate,
  table = "Domestic Legal Provisions",
}: {
  provisionId: string;
  textType: string;
  onHasEnglishTranslationUpdate?: (hasTranslation: boolean) => void;
  table?: TableName;
}) {
  const hasEnglishTranslation = ref(false);
  const showEnglish = ref(true);

  const tableRef = ref(table);
  const idRef = ref(provisionId);

  const {
    data: provisionData,
    isLoading: loading,
    error,
  } = useRecordDetails(tableRef, idRef);

  const title = computed(() => {
    if (!provisionData.value) return "";
    const data = provisionData.value as Record<string, unknown>;
    return table === "Regional Legal Provisions"
      ? (data["Title of the Provision"] as string) || "Unknown Article"
      : (data.Article as string) || "Unknown Article";
  });

  const content = computed(() => {
    if (!provisionData.value) return "";
    const data = provisionData.value as Record<string, unknown>;

    return showEnglish.value
      ? (table === "Regional Legal Provisions"
          ? (data["Full Text"] as string)
          : (data[
              "Full Text of the Provision (English Translation)"
            ] as string)) ||
          (data["Full Text of the Provision (Original Language)"] as string) ||
          "No content available"
      : (data["Full Text of the Provision (Original Language)"] as string) ||
          "No content available";
  });

  const anchorId = computed(() => {
    const articleNumber = title.value
      ? (title.value as string).replace(/\s+/g, "")
      : provisionId.replace(/\s+/g, "");
    return articleNumber;
  });

  watch(
    provisionData,
    (newData) => {
      if (newData) {
        const data = newData as Record<string, unknown>;
        hasEnglishTranslation.value =
          "Full Text of the Provision (English Translation)" in data;

        if (onHasEnglishTranslationUpdate) {
          onHasEnglishTranslationUpdate(hasEnglishTranslation.value);
        }
      }
    },
    { immediate: true },
  );

  function updateContent() {}

  // For backwards compatibility, provide a fetchProvisionDetails function
  function fetchProvisionDetails() {
    // With TanStack Query, this is handled automatically
    // We can update the refs to trigger a refetch if needed
    idRef.value = provisionId;
    tableRef.value = table;
  }

  return {
    title,
    content,
    loading,
    error,
    hasEnglishTranslation,
    showEnglish,
    anchorId,
    fetchProvisionDetails,
    updateContent,
  };
}
