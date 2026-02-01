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
          class="text-cold-purple mt-4 inline-flex items-center gap-1 text-sm hover:underline"
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
      color="error"
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
          <div class="bg-cold-purple/5 rounded-lg p-6">
            <div class="flex items-start gap-4">
              <div
                class="bg-cold-purple/10 flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full"
              >
                <UIcon
                  name="i-heroicons-lock-closed"
                  class="text-cold-purple h-6 w-6"
                />
              </div>
              <div class="flex-1">
                <h3 class="text-cold-night mb-2 font-semibold">
                  Login Required to Use Case Analyzer
                </h3>
                <p class="text-cold-night-alpha mb-4 text-sm">
                  You'll need a free account to use the AI-powered Case
                  Analyzer. We use authentication to prevent automated spam and
                  ensure the integrity of our database. Your account is
                  completely free and takes just moments to create.
                </p>
                <div class="flex flex-wrap gap-3">
                  <a
                    :href="`/auth/login?returnTo=/court-decision/new`"
                    class="bg-cold-purple hover:bg-cold-purple/90 inline-flex items-center gap-2 rounded-lg px-4 py-2 font-semibold !text-white transition-colors"
                  >
                    <UIcon name="i-heroicons-arrow-right-on-rectangle" />
                    Login
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
import { ref, watch, onMounted } from "vue";
import type { JurisdictionOption, AnalysisStepPayload } from "~/types/analyzer";
import { useAnalyzerForm } from "~/composables/useAnalyzerForm";
import { useAnalysisSteps } from "~/composables/useAnalysisSteps";
import { useDocumentUpload } from "~/composables/useDocumentUpload";
import { useCaseAnalyzer } from "~/composables/useCaseAnalyzer";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";
import FileUploadCard from "@/components/case-analyzer/FileUploadCard.vue";
import JurisdictionConfirmCard from "@/components/case-analyzer/JurisdictionConfirmCard.vue";
import AnalysisReviewForm from "@/components/case-analyzer/AnalysisReviewForm.vue";
import AnalysisStepTracker from "@/components/case-analyzer/AnalysisStepTracker.vue";
import PageHero from "@/components/ui/PageHero.vue";
import AnalyzerIllustration from "@/components/case-analyzer/AnalyzerIllustration.vue";

definePageMeta({});

useHead({ title: "AI Case Analyzer — CoLD" });

const user = useUser();
const route = useRoute();

// State
const currentStep = ref<"upload" | "confirm" | "analyzing">("upload");
const error = ref<string | null>(null);
const analysisResults = ref<Record<string, AnalysisStepPayload>>({});
const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);

// Composables
const { findJurisdictionByName } = useJurisdictionLookup();

const {
  selectedFile,
  isUploading,
  currentStep: uploadStep,
  draftId,
  jurisdictionInfo,
  uploadDocument: performUpload,
  reset: resetUpload,
} = useDocumentUpload();

const {
  analysisSteps,
  stepsMap,
  getFieldStatus,
  isFieldLoading,
  updateStepStatus,
  handleUploadStepChange,
  hydrateAnalysisStepsFromResults,
  resetAnalysisSteps,
} = useAnalysisSteps();

const analysis = useCaseAnalyzer(analysisSteps, stepsMap, analysisResults, () =>
  populateEditableForm(),
);

const {
  editableForm,
  isCommonLawJurisdiction,
  populateEditableForm,
  resetEditableForm,
} = useAnalyzerForm(jurisdictionInfo, analysisResults);

// Watch upload step to update step tracker
watch(uploadStep, (step) => {
  handleUploadStepChange(step, jurisdictionInfo.value);
});

// Initialize selectedJurisdiction when jurisdictionInfo changes
watch(
  () => jurisdictionInfo.value?.precise_jurisdiction,
  (preciseJurisdiction) => {
    if (preciseJurisdiction) {
      const match = findJurisdictionByName(preciseJurisdiction);
      if (match) {
        selectedJurisdiction.value = match;
      }
    }
  },
  { immediate: true },
);

// Populate form when analysis completes
watch(
  () => analysis.isAnalyzing.value,
  (isAnalyzing, wasAnalyzing) => {
    if (wasAnalyzing && !isAnalyzing && currentStep.value === "analyzing") {
      populateEditableForm();
    }
  },
);

async function uploadDocument() {
  error.value = null;
  updateStepStatus("document_upload", "in_progress");

  const result = await performUpload();

  if (result.success) {
    currentStep.value = "confirm";
    if (draftId.value) {
      await navigateTo({ query: { draft: draftId.value.toString() } });
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

  if (!resume) {
    resetAnalysisSteps(new Set(["document_upload", "jurisdiction_detection"]));
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
  resetAnalysisSteps();
  navigateTo("/court-decision/new", { replace: true });
}

onMounted(async () => {
  const draftParam = route.query.draft;
  if (draftParam && typeof draftParam === "string") {
    error.value = null;
    const result = await analysis.recoverDraft(draftParam);

    if (result.success && result.data) {
      draftId.value = result.data.draftId;
      if (result.data.fileName) {
        selectedFile.value = new File([], result.data.fileName, {
          type: "application/pdf",
        });
      }
      if (result.data.jurisdictionInfo) {
        jurisdictionInfo.value = result.data.jurisdictionInfo;
      }

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
      currentStep.value = "upload";
      navigateTo("/court-decision/new", { replace: true });
    }
  }
});
</script>
