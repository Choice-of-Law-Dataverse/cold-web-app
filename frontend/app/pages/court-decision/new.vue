<template>
  <div>
    <SubmissionDisclaimer
      :show-autosave-note="false"
      :extra-notes="caseAnalyzerNotes"
    />

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
      <div class="no-print lg:col-span-1">
        <AnalysisStepTracker
          :steps="analysisSteps"
          :is-common-law="isCommonLawJurisdiction"
          :current-phase="stage"
          @retry="handleRetry"
        />
      </div>

      <!-- Main content area -->
      <div class="lg:col-span-2 print:col-span-3">
        <!-- Login Required Notice (shown when not authenticated) -->
        <UCard v-if="!user && stage === 'upload'" class="mb-6">
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
          v-if="user && stage === 'upload'"
          v-model:selected-file="selectedFile"
          :is-uploading="isUploading"
          @upload="uploadDocument"
          @cancel="navigateTo('/court-decision/new')"
          @error="(msg) => (error = msg)"
        />

        <!-- Step 2: Review & Submit -->
        <AnalysisReviewForm
          v-if="stage === 'analyzing'"
          :editable-form="editableForm"
          :document-name="selectedFile?.name || 'Unknown'"
          :selected-jurisdiction="selectedJurisdiction"
          :legal-system-type="jurisdictionInfo?.legal_system_type || ''"
          :is-common-law-jurisdiction="isCommonLawJurisdiction"
          :is-analyzing="isAnalyzing"
          :is-submitting="isSubmitting"
          :is-submitted="isSubmitted"
          :get-field-status="getFieldStatus"
          :is-field-loading="isFieldLoading"
          @submit="submit"
          @reset="resetAnalysis"
          @re-analyze="handleReAnalyze"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import type { JurisdictionOption } from "~/types/analyzer";
import { useCaseAnalysisSession } from "~/composables/useCaseAnalysisSession";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";
import FileUploadCard from "@/components/case-analyzer/FileUploadCard.vue";
import AnalysisReviewForm from "@/components/case-analyzer/AnalysisReviewForm.vue";
import AnalysisStepTracker from "@/components/case-analyzer/AnalysisStepTracker.vue";
import SubmissionDisclaimer, {
  type SubmissionNote,
} from "@/components/ui/SubmissionDisclaimer.vue";

useHead({ title: "AI Case Analyzer — CoLD" });

const caseAnalyzerNotes: SubmissionNote[] = [
  {
    icon: "i-material-symbols:auto-awesome-outline",
    variant: "teal",
    title: "Case Analyzer",
    badge: "AI-Powered",
    description:
      "Upload a court decision and let AI automatically extract jurisdiction, choice of law provisions, and key PIL elements.",
  },
  {
    icon: "i-material-symbols:list-alt-outline",
    variant: "purple",
    title: "View my analyses",
    description:
      "Pick up where you left off — past uploads and drafts stay accessible from your account.",
    to: "/court-decision/my-analyses",
  },
];

const user = useUser();
const route = useRoute();

const {
  stage,
  error,
  selectedFile,
  isUploading,
  draftId,
  jurisdictionInfo,
  analysisSteps,
  getFieldStatus,
  isFieldLoading,
  editableForm,
  isCommonLawJurisdiction,
  isAnalyzing,
  isSubmitting,
  isSubmitted,
  isRecovering,
  analyze,
  reAnalyze,
  submit,
  recover,
  reset,
  uploadDocument: uploadDraft,
} = useCaseAnalysisSession();

const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);
const { findJurisdictionByName, data: jurisdictionOptions } =
  useJurisdictionLookup();

watch(
  [() => jurisdictionInfo.value?.precise_jurisdiction, jurisdictionOptions],
  ([preciseJurisdiction]) => {
    if (preciseJurisdiction) {
      const match = findJurisdictionByName(preciseJurisdiction);
      if (match) {
        selectedJurisdiction.value = match;
      }
    }
  },
  { immediate: true },
);

async function uploadDocument() {
  if (!(await uploadDraft())) return;
  if (draftId.value) {
    await navigateTo({ query: { draft: draftId.value.toString() } });
  }
  await analyze();
}

function handleRetry(_stepName: string) {
  analyze({ resume: true });
}

function handleReAnalyze(
  legalSystemType: string,
  jurisdiction: JurisdictionOption | undefined,
) {
  if (jurisdiction) {
    selectedJurisdiction.value = jurisdiction;
  }
  reAnalyze(legalSystemType, jurisdiction);
}

function resetAnalysis() {
  selectedJurisdiction.value = undefined;
  reset();
  navigateTo("/court-decision/new", { replace: true });
}

onMounted(async () => {
  const draftParam = route.query.draft;
  if (!draftParam || typeof draftParam !== "string") return;
  if (!(await recover(draftParam))) {
    navigateTo("/court-decision/new", { replace: true });
  }
});
</script>
