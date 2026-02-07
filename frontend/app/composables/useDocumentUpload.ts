import { ref } from "vue";
import type { JurisdictionInfo } from "~/types/analyzer";
import { readFileAsBase64 } from "~/utils/fileUtils";
import { streamSSE, type SSEEvent } from "~/composables/useSSEStream";

interface UploadStepData {
  draft_id?: number;
  jurisdiction?: JurisdictionInfo;
}

const stepLabels: Record<string, string> = {
  extracting_text: "Extracted Text",
  detecting_jurisdiction: "Detected Jurisdiction",
  saving_draft: "Saved Draft",
};

export function useDocumentUpload() {
  const selectedFile = ref<File | null>(null);
  const isUploading = ref(false);
  const draftId = ref<number | null>(null);
  const jurisdictionInfo = ref<JurisdictionInfo | null>(null);
  const currentStep = ref<string | null>(null);
  const toast = useToast();

  async function uploadDocument(): Promise<{
    success: boolean;
    error?: string;
  }> {
    if (!selectedFile.value) {
      return { success: false, error: "No file selected" };
    }

    isUploading.value = true;
    currentStep.value = null;

    try {
      const fileContent = await readFileAsBase64(selectedFile.value);
      const blobUrl = `data:application/pdf;base64,${fileContent}`;

      await streamSSE<UploadStepData>({
        url: "/api/proxy/case-analyzer/upload",
        method: "POST",
        body: { file_name: selectedFile.value.name, blob_url: blobUrl },
        stepLabels,
        onEvent: (event: SSEEvent<UploadStepData>) => {
          currentStep.value = event.step;

          if (event.step === "upload_complete" && event.data) {
            draftId.value = event.data.draft_id ?? null;
            jurisdictionInfo.value = event.data.jurisdiction ?? null;
          }

          if (event.step === "detecting_jurisdiction" && event.data) {
            jurisdictionInfo.value =
              (event.data as unknown as JurisdictionInfo) ?? null;
          }
        },
        onError: (error: string) => {
          throw new Error(error);
        },
      });

      return { success: true };
    } catch (err: unknown) {
      console.error("Upload failed:", err);
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Failed to upload document. Please try again.";

      toast.add({
        title: "Upload Failed",
        description: errorMessage,
        color: "error",
        icon: "i-heroicons-x-circle",
        duration: 5000,
      });

      return {
        success: false,
        error: errorMessage,
      };
    } finally {
      isUploading.value = false;
      currentStep.value = null;
    }
  }

  function reset() {
    selectedFile.value = null;
    draftId.value = null;
    jurisdictionInfo.value = null;
    isUploading.value = false;
    currentStep.value = null;
  }

  return {
    selectedFile,
    isUploading,
    currentStep,
    draftId,
    jurisdictionInfo,
    uploadDocument,
    reset,
  };
}
