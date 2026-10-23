import { ref, watch } from "vue";
import type {
  AnalysisStepPayload,
  EditedAnalysisValues,
  JurisdictionInfo,
  JurisdictionOption,
} from "~/types/analyzer";
import { useAnalyzerForm } from "~/composables/useAnalyzerForm";
import { useAnalysisSteps } from "~/composables/useAnalysisSteps";
import { useDocumentUpload } from "~/composables/useDocumentUpload";
import { useCaseAnalyzer } from "~/composables/useCaseAnalyzer";

/**
 * One case-analyzer run: the uploaded document, the streamed analysis steps,
 * their raw results and the editable form built from them. `reset()` returns
 * all of it to the upload stage; navigation stays with the page.
 */
export function useCaseAnalysisSession() {
  const stage = ref<"upload" | "analyzing">("upload");
  const error = ref<string | null>(null);
  const analysisResults = ref<Record<string, AnalysisStepPayload>>({});

  const upload = useDocumentUpload();
  const steps = useAnalysisSteps();
  const form = useAnalyzerForm(upload.jurisdictionInfo, analysisResults);
  const analyzer = useCaseAnalyzer(
    steps.analysisSteps,
    steps.stepsMap,
    analysisResults,
    form.populateEditableForm,
  );

  watch(upload.currentStep, steps.handleUploadStepChange);

  function isFieldLoading(fieldName: keyof EditedAnalysisValues) {
    return steps.isFieldLoading(fieldName, analyzer.isAnalyzing.value);
  }

  function markJurisdictionDetected(info: JurisdictionInfo) {
    steps.updateStepStatus("jurisdiction_detection", "completed", {
      confidence: info.confidence,
      reasoning: info.reasoning,
    });
  }

  /** Uploads the selected file and creates a draft; true on success. */
  async function uploadDocument(): Promise<boolean> {
    error.value = null;
    steps.updateStepStatus("document_upload", "in_progress");
    const result = await upload.uploadDocument();
    if (!result.success) {
      error.value = result.error || "Upload failed";
      steps.updateStepStatus("document_upload", "error");
      return false;
    }
    return true;
  }

  /**
   * Streams the analysis of the current draft into the form. A fresh run
   * discards earlier results; `resume` keeps them and continues.
   */
  async function analyze({
    resume = false,
    jurisdictionConfirmed = false,
  } = {}) {
    const draftId = upload.draftId.value;
    if (!draftId) return;

    stage.value = "analyzing";
    error.value = null;

    if (!resume) {
      steps.resetAnalysisSteps(new Set(["document_upload"]));
      analysisResults.value = {};
    }

    if (upload.jurisdictionInfo.value) {
      markJurisdictionDetected(upload.jurisdictionInfo.value);
    }

    const result = await analyzer.startAnalysis(
      draftId,
      upload.jurisdictionInfo.value,
      resume,
      (jurisdiction) => {
        upload.jurisdictionInfo.value = jurisdiction;
      },
      jurisdictionConfirmed,
    );

    form.populateEditableForm();

    if (!result.success) {
      error.value = result.error || "Analysis failed";
    }
  }

  /** Restarts the analysis with a legal system and jurisdiction set by the user. */
  function reAnalyze(
    legalSystemType: string,
    jurisdiction: JurisdictionOption | undefined,
  ) {
    const info: JurisdictionInfo = upload.jurisdictionInfo.value ?? {
      legal_system_type: "",
      precise_jurisdiction: "",
      jurisdiction_code: "",
      confidence: "high",
      reasoning: "Jurisdiction set manually by the user during review.",
    };
    info.legal_system_type = legalSystemType;
    if (jurisdiction) {
      info.precise_jurisdiction = jurisdiction.name || "";
      info.jurisdiction_code = jurisdiction.coldId || info.jurisdiction_code;
    }
    upload.jurisdictionInfo.value = info;
    analysisResults.value = {};
    form.resetEditableForm();
    return analyze({ jurisdictionConfirmed: true });
  }

  async function submit() {
    const draftId = upload.draftId.value;
    if (!draftId) {
      error.value = "No analysis data available";
      return;
    }

    const result = await analyzer.submitSuggestion(
      draftId,
      upload.jurisdictionInfo.value,
      analysisResults.value,
      form.editableForm,
    );

    if (!result.success) {
      error.value = result.error || "Submission failed";
    }
  }

  /**
   * Restores a saved draft. A completed draft opens for review; an
   * unfinished one resumes its analysis. False when the draft cannot be
   * loaded, with `error` explaining why.
   */
  async function recover(draftParam: string): Promise<boolean> {
    error.value = null;
    const result = await analyzer.recoverDraft(draftParam);

    if (!result.success || !result.data) {
      error.value = result.error || "Failed to recover draft";
      stage.value = "upload";
      return false;
    }

    const draft = result.data;
    upload.draftId.value = draft.draftId;
    if (draft.fileName) {
      upload.selectedFile.value = new File([], draft.fileName, {
        type: "application/pdf",
      });
    }
    if (draft.jurisdictionInfo) {
      upload.jurisdictionInfo.value = draft.jurisdictionInfo;
    }
    if (Object.keys(draft.analyzerData).length > 0) {
      steps.hydrateAnalysisStepsFromResults(draft.analyzerData);
    }
    steps.updateStepStatus("document_upload", "completed");
    if (draft.jurisdictionInfo) {
      markJurisdictionDetected(draft.jurisdictionInfo);
    }

    if (draft.status === "completed") {
      stage.value = "analyzing";
      form.populateEditableForm();
    } else {
      await analyze({ resume: true });
    }
    return true;
  }

  function reset() {
    stage.value = "upload";
    error.value = null;
    analysisResults.value = {};
    upload.reset();
    form.resetEditableForm();
    analyzer.reset();
    steps.resetAnalysisSteps();
  }

  return {
    stage,
    error,
    selectedFile: upload.selectedFile,
    isUploading: upload.isUploading,
    draftId: upload.draftId,
    jurisdictionInfo: upload.jurisdictionInfo,
    analysisSteps: steps.analysisSteps,
    getFieldStatus: steps.getFieldStatus,
    isFieldLoading,
    editableForm: form.editableForm,
    isCommonLawJurisdiction: form.isCommonLawJurisdiction,
    isAnalyzing: analyzer.isAnalyzing,
    isSubmitting: analyzer.isSubmitting,
    isSubmitted: analyzer.isSubmitted,
    isRecovering: analyzer.isRecovering,
    uploadDocument,
    analyze,
    reAnalyze,
    submit,
    recover,
    reset,
  };
}
