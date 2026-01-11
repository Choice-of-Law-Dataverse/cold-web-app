<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mx-auto max-w-5xl">
      <!-- Page Header -->
      <PageHero
        title="Case Analyzer"
        subtitle="Upload a court decision and let AI automatically extract jurisdiction, choice of law provisions, and key PIL elements."
        badge="AI-Powered"
      >
        <template #illustration>
          <AnalyzerIllustration />
        </template>
      </PageHero>

      <!-- Error Display -->
      <UAlert
        v-if="error"
        color="red"
        icon="i-material-symbols:error"
        :title="error"
        class="mb-6"
        :close-button="{
          icon: 'i-heroicons-x-mark',
          color: 'red',
          variant: 'link',
        }"
        @close="error = null"
      />

      <!-- Recovery Loading State -->
      <div
        v-if="isRecovering"
        class="mb-6 flex items-center justify-center py-12"
      >
        <div class="text-center">
          <UIcon
            name="i-heroicons-arrow-path"
            class="text-primary-500 mb-4 h-8 w-8 animate-spin"
          />
          <p class="text-gray-600">Recovering your draft...</p>
        </div>
      </div>

      <!-- Two column layout throughout -->
      <div v-if="!isRecovering" class="grid gap-6 lg:grid-cols-3">
        <!-- Sidebar: Progress tracker (always visible) -->
        <div class="lg:col-span-1">
          <AnalysisStepTracker
            :steps="analysisSteps"
            :is-common-law="isCommonLawJurisdiction"
            :current-phase="currentStep"
            @retry="handleRetry"
          />
        </div>

        <!-- Main content area -->
        <div class="lg:col-span-2">
          <!-- Step 1: File Upload -->
          <FileUploadCard
            v-if="currentStep === 'upload'"
            v-model:selected-file="selectedFile"
            :is-uploading="isUploading"
            @upload="uploadDocument"
            @cancel="navigateTo('/court-decision/new')"
            @error="(msg) => (error = msg)"
          />

          <!-- Step 2: Jurisdiction Confirmation -->
          <JurisdictionConfirmCard
            v-if="currentStep === 'confirm'"
            v-model:selected-jurisdiction="selectedJurisdiction"
            :document-name="selectedFile?.name || 'Unknown'"
            :jurisdiction-info="jurisdictionInfo"
            :is-loading="analysis.isAnalyzing.value"
            @continue="confirmAndAnalyze(false)"
            @reset="resetAnalysis"
            @jurisdiction-updated="onJurisdictionSelected"
            @legal-system-updated="onLegalSystemSelected"
          />

          <!-- Step 3: Review & Submit -->
          <AnalysisReviewForm
            v-if="currentStep === 'analyzing'"
            v-model:editable-form="editableForm"
            :document-name="selectedFile?.name || 'Unknown'"
            :selected-jurisdiction="selectedJurisdiction"
            :is-common-law-jurisdiction="isCommonLawJurisdiction"
            :is-analyzing="analysis.isAnalyzing.value"
            :is-submitting="analysis.isSubmitting.value"
            :is-submitted="analysis.isSubmitted.value"
            :get-field-status="getFieldStatus"
            :is-field-loading="isFieldLoading"
            @submit="submitAnalyzerSuggestion"
            @reset="resetAnalysis"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watchEffect, onMounted } from "vue";
import type { JurisdictionOption, AnalysisStepPayload } from "~/types/analyzer";
import { useAnalyzerForm } from "~/composables/useAnalyzerForm";
import { useAnalysisSteps } from "~/composables/useAnalysisSteps";
import { useDocumentUpload } from "~/composables/useDocumentUpload";
import { useCaseAnalyzer } from "~/composables/useCaseAnalyzer";
import { useJurisdictions } from "@/composables/useJurisdictions";
import FileUploadCard from "@/components/case-analyzer/FileUploadCard.vue";
import JurisdictionConfirmCard from "@/components/case-analyzer/JurisdictionConfirmCard.vue";
import AnalysisReviewForm from "@/components/case-analyzer/AnalysisReviewForm.vue";
import AnalysisStepTracker from "@/components/case-analyzer/AnalysisStepTracker.vue";
import PageHero from "@/components/ui/PageHero.vue";
import AnalyzerIllustration from "@/components/case-analyzer/AnalyzerIllustration.vue";

definePageMeta({
  middleware: ["auth"],
});

useHead({ title: "AI Case Analyzer — CoLD" });

// Route for draft recovery
const route = useRoute();

// State
const currentStep = ref<"upload" | "confirm" | "analyzing">("upload");
const error = ref<string | null>(null);
const analysisResults = ref<Record<string, AnalysisStepPayload>>({});
const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);
const isRecovering = ref(false);

// Jurisdictions for selector
const { data: jurisdictions } = useJurisdictions();

// Composables
const {
  selectedFile,
  isUploading,
  draftId,
  jurisdictionInfo,
  uploadDocument: performUpload,
  reset: resetUpload,
} = useDocumentUpload();

const { analysisSteps, getFieldStatus, isFieldLoading } = useAnalysisSteps();

const analysis = useCaseAnalyzer(analysisSteps, analysisResults, () =>
  populateEditableForm(),
);

const {
  editableForm,
  isCommonLawJurisdiction,
  populateEditableForm,
  resetEditableForm,
} = useAnalyzerForm(jurisdictionInfo, analysisResults);

// Helper to update a specific step's status
function updateStepStatus(
  stepName: string,
  status: "pending" | "in_progress" | "completed" | "error",
  data?: { confidence?: string; reasoning?: string },
) {
  const step = analysisSteps.value.find((s) => s.name === stepName);
  if (step) {
    step.status = status;
    if (data) {
      step.confidence = data.confidence || null;
      step.reasoning = data.reasoning || null;
    }
  }
}

// Populate form when analysis completes
watchEffect(() => {
  if (currentStep.value === "analyzing" && !analysis.isAnalyzing.value) {
    populateEditableForm();
  }
});

// Initialize selectedJurisdiction when jurisdictionInfo changes
watchEffect(() => {
  if (jurisdictionInfo.value && jurisdictions.value) {
    const match = jurisdictions.value.find(
      (j: JurisdictionOption) =>
        j.Name === jurisdictionInfo.value?.precise_jurisdiction,
    );
    if (match) {
      selectedJurisdiction.value = match;
    }
  }
});

// Document upload handler
async function uploadDocument() {
  error.value = null;
  updateStepStatus("document_upload", "in_progress");

  const result = await performUpload(
    () => updateStepStatus("document_upload", "in_progress"),
    () => {
      updateStepStatus("document_upload", "completed");
      updateStepStatus("jurisdiction_detection", "in_progress");
    },
    () => {
      if (jurisdictionInfo.value) {
        updateStepStatus("jurisdiction_detection", "completed", {
          confidence: jurisdictionInfo.value.confidence,
          reasoning: jurisdictionInfo.value.reasoning,
        });
      }
    },
  );

  if (result.success) {
    currentStep.value = "confirm";
    // Add draft_id to URL for bookmarking/returning to draft
    if (draftId.value) {
      await navigateTo({
        query: { draft: draftId.value.toString() },
      });
    }
  } else {
    error.value = result.error || "Upload failed";
    updateStepStatus("document_upload", "error");
  }
}

function onJurisdictionSelected(jurisdiction: JurisdictionOption) {
  if (jurisdictionInfo.value) {
    jurisdictionInfo.value.precise_jurisdiction = jurisdiction.Name || "";
    jurisdictionInfo.value.jurisdiction_code =
      jurisdiction.alpha3Code || jurisdictionInfo.value.jurisdiction_code;
  }
}

function onLegalSystemSelected(legalSystemType: string) {
  if (jurisdictionInfo.value) {
    jurisdictionInfo.value.legal_system_type = legalSystemType;
  }
}

async function confirmAndAnalyze(resume = false) {
  if (!draftId.value || !jurisdictionInfo.value) return;

  currentStep.value = "analyzing";
  error.value = null;

  // Reset only analysis steps (not upload/jurisdiction) if not resuming
  if (!resume) {
    analysisSteps.value.forEach((step) => {
      if (!["document_upload", "jurisdiction_detection"].includes(step.name)) {
        step.status = "pending";
        step.confidence = null;
        step.reasoning = null;
        step.error = null;
      }
    });
  }

  const result = await analysis.startAnalysis(
    draftId.value,
    jurisdictionInfo.value,
    resume,
  );

  if (!result.success) {
    error.value = result.error || "Analysis failed";
  }
}

function handleRetry(_stepName: string) {
  confirmAndAnalyze(true);
}

async function submitAnalyzerSuggestion() {
  if (!draftId.value) {
    error.value = "No analysis data available";
    return;
  }

  const result = await analysis.submitSuggestion(
    draftId.value,
    jurisdictionInfo.value,
    analysisResults.value,
    editableForm,
  );

  if (!result.success) {
    error.value = result.error || "Submission failed";
  }
}

function resetAnalysis() {
  currentStep.value = "upload";
  selectedJurisdiction.value = undefined;
  analysisResults.value = {};
  error.value = null;
  resetUpload();
  resetEditableForm();
  analysis.reset();
  analysisSteps.value.forEach((step) => {
    step.status = "pending";
    step.confidence = null;
    step.reasoning = null;
    step.error = null;
  });
}

// Draft recovery on page load
async function recoverDraft(draftIdParam: string) {
  const draftIdNum = parseInt(draftIdParam, 10);
  if (isNaN(draftIdNum)) return;

  isRecovering.value = true;
  error.value = null;

  try {
    const { data, error: fetchError } = await useFetch<{
      draft_id: number;
      status: string;
      file_name: string | null;
      pdf_url: string | null;
      jurisdiction_info: {
        precise_jurisdiction?: string;
        jurisdiction_code?: string;
        legal_system_type?: string;
        confidence?: string;
        reasoning?: string;
      } | null;
      analyzer_data: Record<string, AnalysisStepPayload>;
      case_citation: string | null;
    }>(`/api/proxy/case-analyzer/draft/${draftIdNum}`);

    if (fetchError.value) {
      // If 400, draft was already submitted - show message and stay on upload
      if (fetchError.value.statusCode === 400) {
        error.value =
          "This draft has already been submitted for review. Start a new analysis.";
        return;
      }
      throw new Error(fetchError.value.message || "Failed to recover draft");
    }

    if (!data.value) {
      error.value = "Draft not found";
      return;
    }

    const draft = data.value;

    // Restore draft ID
    draftId.value = draft.draft_id;

    // Restore file info (create a fake file reference for display)
    if (draft.file_name) {
      selectedFile.value = new File([], draft.file_name, {
        type: "application/pdf",
      });
    }

    // Restore jurisdiction info
    if (draft.jurisdiction_info) {
      jurisdictionInfo.value = {
        precise_jurisdiction:
          draft.jurisdiction_info.precise_jurisdiction || "",
        jurisdiction_code: draft.jurisdiction_info.jurisdiction_code || "",
        legal_system_type: draft.jurisdiction_info.legal_system_type || "",
        confidence: draft.jurisdiction_info.confidence || "",
        reasoning: draft.jurisdiction_info.reasoning || "",
      };
    }

    // Restore analysis results
    if (draft.analyzer_data && Object.keys(draft.analyzer_data).length > 0) {
      analysisResults.value = draft.analyzer_data;

      // Update step statuses based on analyzer_data
      for (const [stepName, stepData] of Object.entries(draft.analyzer_data)) {
        const step = analysisSteps.value.find((s) => s.name === stepName);
        if (step && stepData) {
          step.status = "completed";
          const payload = stepData as AnalysisStepPayload;
          step.confidence =
            typeof payload.confidence === "string" ? payload.confidence : null;
          step.reasoning =
            typeof payload.reasoning === "string" ? payload.reasoning : null;
        }
      }
    }

    // Mark upload and jurisdiction as completed
    updateStepStatus("document_upload", "completed");
    if (draft.jurisdiction_info) {
      updateStepStatus("jurisdiction_detection", "completed", {
        confidence: draft.jurisdiction_info.confidence,
        reasoning: draft.jurisdiction_info.reasoning,
      });
    }

    // Determine which step to show based on status and data
    if (draft.status === "completed" || draft.status === "analyzing") {
      // Has analysis data - go to review form
      currentStep.value = "analyzing";
      populateEditableForm();
    } else if (draft.jurisdiction_info) {
      // Has jurisdiction but no analysis - go to confirm
      currentStep.value = "confirm";
    } else {
      // No data - stay on upload
      currentStep.value = "upload";
    }
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : "Failed to recover draft";
  } finally {
    isRecovering.value = false;
  }
}

// Check for draft parameter on mount
onMounted(() => {
  const draftParam = route.query.draft;
  if (draftParam && typeof draftParam === "string") {
    recoverDraft(draftParam);
  }
});
</script>
