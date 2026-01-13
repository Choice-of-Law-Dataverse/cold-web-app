<template>
  <div class="py-12">
    <!-- Page Header -->
    <PageHero
      title="Case Analyzer"
      subtitle="Upload a court decision and let AI automatically extract jurisdiction, choice of law provisions, and key PIL elements."
      badge="AI-Powered"
    >
      <template #content>
        <NuxtLink
          to="/court-decision/my-analyses"
          class="mt-4 inline-flex items-center gap-1 text-sm text-cold-purple hover:underline"
        >
          <UIcon name="i-heroicons-document-text" class="h-4 w-4" />
          View My Analyses
        </NuxtLink>
      </template>
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
      v-if="analysis.isRecovering.value"
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
    <div v-if="!analysis.isRecovering.value" class="grid gap-6 lg:grid-cols-3">
      <!-- Sidebar: Progress tracker (always visible) -->
      <div class="no-print lg:col-span-1">
        <AnalysisStepTracker
          :steps="analysisSteps"
          :is-common-law="isCommonLawJurisdiction"
          :current-phase="currentStep"
          @retry="handleRetry"
        />
      </div>

      <!-- Main content area -->
      <div class="lg:col-span-2 print:col-span-3">
        <!-- Login Required Notice (shown when not authenticated) -->
        <UCard v-if="!user && currentStep === 'upload'" class="mb-6">
          <div class="rounded-lg bg-cold-purple/5 p-6">
            <div class="flex items-start gap-4">
              <div
                class="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-cold-purple/10"
              >
                <UIcon
                  name="i-heroicons-lock-closed"
                  class="h-6 w-6 text-cold-purple"
                />
              </div>
              <div class="flex-1">
                <h3 class="mb-2 font-semibold text-cold-night">
                  Login Required to Use Case Analyzer
                </h3>
                <p class="mb-4 text-sm text-cold-night-alpha">
                  You'll need a free account to use the AI-powered Case
                  Analyzer. We use authentication to prevent automated spam and
                  ensure the integrity of our database. Your account is
                  completely free and takes just moments to create.
                </p>
                <div class="flex flex-wrap gap-3">
                  <a
                    :href="`/auth/login?returnTo=/court-decision/new`"
                    class="inline-flex items-center gap-2 rounded-lg bg-cold-purple px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-cold-purple/90"
                  >
                    <UIcon name="i-heroicons-arrow-right-on-rectangle" />
                    Login
                  </a>
                  <a
                    :href="`/auth/login?screen_hint=signup&returnTo=/court-decision/new`"
                    class="inline-flex items-center gap-2 rounded-lg border border-cold-purple px-4 py-2 text-sm font-semibold text-cold-purple transition-colors hover:bg-cold-purple/5"
                  >
                    <UIcon name="i-heroicons-user-plus" />
                    Create Free Account
                  </a>
                </div>
              </div>
            </div>
          </div>
        </UCard>

        <!-- Step 1: File Upload (shown when authenticated) -->
        <FileUploadCard
          v-if="user && currentStep === 'upload'"
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

definePageMeta({});

useHead({ title: "AI Case Analyzer — CoLD" });

// Check if user is authenticated
const user = useUser();

// Route for draft recovery
const route = useRoute();

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
  draftId,
  jurisdictionInfo,
  uploadDocument: performUpload,
  reset: resetUpload,
} = useDocumentUpload();

const {
  analysisSteps,
  getFieldStatus,
  isFieldLoading,
  hydrateAnalysisStepsFromResults,
} = useAnalysisSteps();

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
  navigateTo("/court-decision/new", { replace: true });
}

onMounted(async () => {
  const draftParam = route.query.draft;
  if (draftParam && typeof draftParam === "string") {
    error.value = null;
    const result = await analysis.recoverDraft(draftParam);

    if (result.success && result.data) {
      // Restore useDocumentUpload state
      draftId.value = result.data.draftId;
      if (result.data.fileName) {
        selectedFile.value = new File([], result.data.fileName, {
          type: "application/pdf",
        });
      }
      if (result.data.jurisdictionInfo) {
        jurisdictionInfo.value = result.data.jurisdictionInfo;
      }

      // Hydrate analysis steps from recovered data
      if (Object.keys(result.data.analyzerData).length > 0) {
        hydrateAnalysisStepsFromResults(result.data.analyzerData);
      }
      updateStepStatus("document_upload", "completed");
      if (result.data.jurisdictionInfo) {
        updateStepStatus("jurisdiction_detection", "completed", {
          confidence: result.data.jurisdictionInfo.confidence,
          reasoning: result.data.jurisdictionInfo.reasoning,
        });
      }

      // Determine which step to show based on status and data
      if (
        result.data.status === "completed" ||
        result.data.status === "analyzing"
      ) {
        currentStep.value = "analyzing";
        populateEditableForm();
      } else if (result.data.jurisdictionInfo) {
        currentStep.value = "confirm";
      } else {
        currentStep.value = "upload";
      }
    } else {
      error.value = result.error || "Failed to recover draft";
      // Reset to upload step and clear URL to provide a clean starting point
      currentStep.value = "upload";
      navigateTo("/court-decision/new", { replace: true });
    }
  }
});
</script>
