import { ref } from "vue";
import type { JurisdictionInfo } from "~/types/analyzer";
import { readFileAsBase64 } from "~/utils/fileUtils";
import { extractErrorMessage } from "~/utils/analyzerPayloadParser";

export function useDocumentUpload() {
  const selectedFile = ref<File | null>(null);
  const isUploading = ref(false);
  const correlationId = ref<string | null>(null);
  const draftId = ref<number | null>(null);
  const jurisdictionInfo = ref<JurisdictionInfo | null>(null);

  async function uploadDocument(
    onUploadStart?: () => void,
    onUploadComplete?: () => void,
    onJurisdictionDetected?: () => void,
  ): Promise<{ success: boolean; error?: string }> {
    if (!selectedFile.value) {
      return { success: false, error: "No file selected" };
    }

    isUploading.value = true;
    onUploadStart?.();

    try {
      const fileContent = await readFileAsBase64(selectedFile.value);

      const useDirectUpload = true;
      let blob_url: string;

      if (useDirectUpload) {
        blob_url = `data:application/pdf;base64,${fileContent}`;
      } else {
        const uploadResponse = await $fetch<{
          blob_url: string;
          blob_name: string;
        }>("/api/upload-temp", {
          method: "POST",
          body: {
            file_name: selectedFile.value.name,
            file_content_base64: fileContent,
          },
        });
        blob_url = uploadResponse.blob_url;
      }

      onUploadComplete?.();

      const data = await $fetch<{
        correlation_id: string;
        draft_id: number;
        jurisdiction: JurisdictionInfo;
      }>("/api/proxy/case-analyzer/upload", {
        method: "POST",
        body: {
          file_name: selectedFile.value.name,
          blob_url,
        },
      });

      correlationId.value = data.correlation_id;
      draftId.value = data.draft_id;
      jurisdictionInfo.value = data.jurisdiction;

      onJurisdictionDetected?.();

      return { success: true };
    } catch (err: unknown) {
      console.error("Upload failed:", err);
      return {
        success: false,
        error:
          extractErrorMessage(err) ||
          "Failed to upload document. Please try again.",
      };
    } finally {
      isUploading.value = false;
    }
  }

  function reset() {
    selectedFile.value = null;
    correlationId.value = null;
    draftId.value = null;
    jurisdictionInfo.value = null;
    isUploading.value = false;
  }

  return {
    selectedFile,
    isUploading,
    correlationId,
    draftId,
    jurisdictionInfo,
    uploadDocument,
    reset,
  };
}
