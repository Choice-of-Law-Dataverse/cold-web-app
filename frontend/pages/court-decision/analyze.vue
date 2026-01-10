<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mx-auto max-w-5xl">
      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center gap-6">
          <div class="flex-1">
            <h1 class="text-2xl font-bold">AI Case Analyzer</h1>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Upload a court decision to extract PIL elements automatically
            </p>
          </div>
          <div class="hidden md:block">
            <svg
              width="120"
              height="120"
              viewBox="0 0 120 120"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              class="text-cold-teal/20"
            >
              <!-- Document shape -->
              <rect
                x="20"
                y="15"
                width="60"
                height="80"
                rx="4"
                fill="currentColor"
                stroke="currentColor"
                stroke-width="2"
              />
              <rect
                x="25"
                y="20"
                width="50"
                height="70"
                rx="2"
                fill="white"
                class="dark:fill-gray-900"
              />
              <!-- Document lines -->
              <line
                x1="32"
                y1="30"
                x2="68"
                y2="30"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
              <line
                x1="32"
                y1="40"
                x2="68"
                y2="40"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
              <line
                x1="32"
                y1="50"
                x2="60"
                y2="50"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
              <!-- AI sparkle -->
              <circle
                cx="85"
                cy="35"
                r="20"
                fill="currentColor"
                class="text-cold-teal"
              />
              <path
                d="M85 25 L87 32 L94 35 L87 38 L85 45 L83 38 L76 35 L83 32 Z"
                fill="white"
                class="dark:fill-gray-900"
              />
              <!-- Magnifying glass -->
              <circle
                cx="65"
                cy="70"
                r="15"
                fill="none"
                stroke="currentColor"
                stroke-width="3"
                class="text-cold-teal"
              />
              <line
                x1="76"
                y1="81"
                x2="88"
                y2="93"
                stroke="currentColor"
                stroke-width="3"
                stroke-linecap="round"
                class="text-cold-teal"
              />
            </svg>
          </div>
        </div>
      </div>

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

      <!-- Two column layout throughout -->
      <div class="grid gap-6 lg:grid-cols-3">
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
import { ref, watchEffect } from "vue";
import type { JurisdictionOption, AnalysisStepPayload } from "~/types/analyzer";
import { useAnalyzerForm } from "~/composables/useAnalyzerForm";
import { useAnalysisSteps } from "~/composables/useAnalysisSteps";
import { useDocumentUpload } from "~/composables/useDocumentUpload";
import { useCaseAnalysis } from "~/composables/useCaseAnalysis";
import { useJurisdictions } from "@/composables/useJurisdictions";
import FileUploadCard from "@/components/case-analysis/FileUploadCard.vue";
import JurisdictionConfirmCard from "@/components/case-analysis/JurisdictionConfirmCard.vue";
import AnalysisReviewForm from "@/components/case-analysis/AnalysisReviewForm.vue";
import AnalysisStepTracker from "@/components/case-analysis/AnalysisStepTracker.vue";

definePageMeta({
  middleware: ["auth"],
});

useHead({ title: "AI Case Analyzer — CoLD" });

// State
const currentStep = ref<"upload" | "confirm" | "analyzing">("upload");
const error = ref<string | null>(null);
const analysisResults = ref<Record<string, AnalysisStepPayload>>({});
const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);

// Jurisdictions for selector
const { data: jurisdictions } = useJurisdictions();

// Composables
const {
  selectedFile,
  isUploading,
  correlationId,
  jurisdictionInfo,
  uploadDocument: performUpload,
  reset: resetUpload,
} = useDocumentUpload();

const { analysisSteps, getFieldStatus, isFieldLoading } = useAnalysisSteps();

const analysis = useCaseAnalysis(analysisSteps, analysisResults, () =>
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

async function confirmAndAnalyze(resume = false) {
  if (!correlationId.value || !jurisdictionInfo.value) return;

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
    correlationId.value,
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
  if (!correlationId.value) {
    error.value = "No analysis data available";
    return;
  }

  const result = await analysis.submitSuggestion(
    correlationId.value,
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
</script>
