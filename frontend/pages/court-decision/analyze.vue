<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mx-auto max-w-5xl">
      <!-- Page Header -->
      <div class="mb-6">
        <h1 class="text-2xl font-bold">AI Case Analyzer</h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Upload a court decision to extract PIL elements automatically
        </p>
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
          <CaseAnalysisStepTracker
            :steps="analysisSteps"
            :is-common-law="isCommonLawJurisdiction"
            :current-phase="currentStep"
            @retry="handleRetry"
          />
        </div>

        <!-- Main content area -->
        <div class="lg:col-span-2">
          <!-- Step 1: File Upload -->
          <UCard v-if="currentStep === 'upload'">
            <template #header>
              <h3 class="font-semibold">Upload Document</h3>
            </template>

            <div
              class="hover:border-primary cursor-pointer rounded-lg border-2 border-dashed border-gray-300 p-8 text-center transition-colors dark:border-gray-600"
              :class="{
                'border-primary bg-primary/5': isDragging || selectedFile,
                'pointer-events-none opacity-60': isUploading,
              }"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleFileDrop"
              @click="!isUploading && fileInput?.click()"
            >
              <input
                ref="fileInput"
                type="file"
                accept=".pdf"
                class="hidden"
                @change="handleFileSelect"
              />

              <UIcon
                :name="
                  selectedFile
                    ? 'i-heroicons-document-check'
                    : 'i-heroicons-arrow-up-tray'
                "
                class="mx-auto mb-3 h-10 w-10"
                :class="selectedFile ? 'text-primary' : 'text-gray-400'"
              />

              <div v-if="!selectedFile">
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Drag and drop your PDF here, or
                  <span class="text-primary font-medium">browse</span>
                </p>
                <p class="mt-1 text-xs text-gray-500">PDF files only</p>
              </div>

              <div v-else>
                <p class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ selectedFile.name }}
                </p>
                <p class="mt-1 text-xs text-gray-500">
                  {{ formatFileSize(selectedFile.size) }} - Click to change
                </p>
              </div>
            </div>

            <template #footer>
              <div class="flex items-center justify-end gap-3">
                <UButton
                  variant="ghost"
                  color="gray"
                  @click="navigateTo('/court-decision/new')"
                >
                  Cancel
                </UButton>
                <UButton
                  color="primary"
                  :disabled="!selectedFile || isUploading"
                  :loading="isUploading"
                  @click="uploadDocument"
                >
                  Upload and Analyze
                </UButton>
              </div>
            </template>
          </UCard>

          <!-- Step 2: Jurisdiction Confirmation -->
          <UCard v-if="currentStep === 'confirm'">
            <template #header>
              <h3 class="font-semibold">Confirm Jurisdiction</h3>
            </template>

            <div v-if="jurisdictionInfo" class="space-y-6">
              <UFormGroup label="Legal System Type">
                <UInput
                  :model-value="jurisdictionInfo.legal_system_type"
                  readonly
                />
                <template #hint>
                  <span
                    v-if="jurisdictionInfo.confidence"
                    class="text-xs text-cold-teal"
                  >
                    {{ jurisdictionInfo.confidence }} confidence
                  </span>
                </template>
              </UFormGroup>

              <UFormGroup label="Jurisdiction">
                <JurisdictionSelectMenu
                  v-model="selectedJurisdiction"
                  :countries="jurisdictions || []"
                  placeholder="Select jurisdiction"
                  @country-selected="onJurisdictionSelected"
                />
              </UFormGroup>
            </div>

            <template #footer>
              <div class="flex items-center justify-end gap-3">
                <UButton variant="ghost" color="gray" @click="resetAnalysis">
                  Start Over
                </UButton>
                <UButton
                  color="primary"
                  :loading="isAnalyzing"
                  @click="confirmAndAnalyze(false)"
                >
                  Continue Analysis
                </UButton>
              </div>
            </template>
          </UCard>

          <!-- Step 3: Review & Submit -->
          <UCard v-if="currentStep === 'analyzing'">
            <template #header>
              <h3 class="font-semibold">
                {{ isAnalyzing ? "Extracting Data..." : "Review & Submit" }}
              </h3>
            </template>

            <div class="space-y-5">
              <UFormGroup>
                <template #label>
                  <span class="flex items-center gap-2">
                    Case Citation
                    <ConfidenceIndicator
                      :is-loading="isFieldLoading('caseCitation')"
                      :field-status="getFieldStatus('caseCitation')"
                    />
                  </span>
                </template>
                <UInput
                  v-model="editableForm.caseCitation"
                  :disabled="isFieldDisabled('caseCitation')"
                />
              </UFormGroup>

              <UFormGroup>
                <template #label>
                  <span class="flex items-center gap-2">
                    Choice of Law Sections
                    <ConfidenceIndicator
                      :is-loading="isFieldLoading('choiceOfLawSections')"
                      :field-status="getFieldStatus('choiceOfLawSections')"
                    />
                  </span>
                </template>
                <UTextarea
                  v-model="editableForm.choiceOfLawSections"
                  :disabled="isFieldDisabled('choiceOfLawSections')"
                  :rows="3"
                />
              </UFormGroup>

              <UFormGroup>
                <template #label>
                  <span class="flex items-center gap-2">
                    Themes
                    <ConfidenceIndicator
                      :is-loading="isFieldLoading('themes')"
                      :field-status="getFieldStatus('themes')"
                    />
                  </span>
                </template>
                <UTextarea
                  v-model="editableForm.themes"
                  :disabled="isFieldDisabled('themes')"
                  :rows="2"
                />
              </UFormGroup>

              <UFormGroup>
                <template #label>
                  <span class="flex items-center gap-2">
                    Relevant Facts
                    <ConfidenceIndicator
                      :is-loading="isFieldLoading('caseRelevantFacts')"
                      :field-status="getFieldStatus('caseRelevantFacts')"
                    />
                  </span>
                </template>
                <UTextarea
                  v-model="editableForm.caseRelevantFacts"
                  :disabled="isFieldDisabled('caseRelevantFacts')"
                  :rows="4"
                />
              </UFormGroup>

              <UFormGroup>
                <template #label>
                  <span class="flex items-center gap-2">
                    PIL Provisions
                    <ConfidenceIndicator
                      :is-loading="isFieldLoading('casePILProvisions')"
                      :field-status="getFieldStatus('casePILProvisions')"
                    />
                  </span>
                </template>
                <UTextarea
                  v-model="editableForm.casePILProvisions"
                  :disabled="isFieldDisabled('casePILProvisions')"
                  :rows="2"
                />
              </UFormGroup>

              <UFormGroup>
                <template #label>
                  <span class="flex items-center gap-2">
                    Choice of Law Issue
                    <ConfidenceIndicator
                      :is-loading="isFieldLoading('caseChoiceofLawIssue')"
                      :field-status="getFieldStatus('caseChoiceofLawIssue')"
                    />
                  </span>
                </template>
                <UTextarea
                  v-model="editableForm.caseChoiceofLawIssue"
                  :disabled="isFieldDisabled('caseChoiceofLawIssue')"
                  :rows="3"
                />
              </UFormGroup>

              <UFormGroup>
                <template #label>
                  <span class="flex items-center gap-2">
                    Court's Position
                    <ConfidenceIndicator
                      :is-loading="isFieldLoading('caseCourtsPosition')"
                      :field-status="getFieldStatus('caseCourtsPosition')"
                    />
                  </span>
                </template>
                <UTextarea
                  v-model="editableForm.caseCourtsPosition"
                  :disabled="isFieldDisabled('caseCourtsPosition')"
                  :rows="3"
                />
              </UFormGroup>

              <UFormGroup v-if="isCommonLawJurisdiction">
                <template #label>
                  <span class="flex items-center gap-2">
                    Obiter Dicta
                    <ConfidenceIndicator
                      :is-loading="isFieldLoading('caseObiterDicta')"
                      :field-status="getFieldStatus('caseObiterDicta')"
                    />
                  </span>
                </template>
                <UTextarea
                  v-model="editableForm.caseObiterDicta"
                  :disabled="isFieldDisabled('caseObiterDicta')"
                  :rows="3"
                />
              </UFormGroup>

              <UFormGroup v-if="isCommonLawJurisdiction">
                <template #label>
                  <span class="flex items-center gap-2">
                    Dissenting Opinions
                    <ConfidenceIndicator
                      :is-loading="isFieldLoading('caseDissentingOpinions')"
                      :field-status="getFieldStatus('caseDissentingOpinions')"
                    />
                  </span>
                </template>
                <UTextarea
                  v-model="editableForm.caseDissentingOpinions"
                  :disabled="isFieldDisabled('caseDissentingOpinions')"
                  :rows="3"
                />
              </UFormGroup>

              <UFormGroup>
                <template #label>
                  <span class="flex items-center gap-2">
                    Abstract
                    <ConfidenceIndicator
                      :is-loading="isFieldLoading('caseAbstract')"
                      :field-status="getFieldStatus('caseAbstract')"
                    />
                  </span>
                </template>
                <UTextarea
                  v-model="editableForm.caseAbstract"
                  :disabled="isFieldDisabled('caseAbstract')"
                  :rows="4"
                />
              </UFormGroup>
            </div>

            <template #footer>
              <div class="flex items-center justify-end gap-3">
                <UButton variant="ghost" color="gray" @click="resetAnalysis">
                  Start Over
                </UButton>
                <UButton
                  color="primary"
                  :loading="isSubmitting"
                  :disabled="isAnalyzing || isSubmitted"
                  @click="submitAnalyzerSuggestion"
                >
                  {{ isSubmitted ? "Submitted" : "Submit for Review" }}
                </UButton>
              </div>
            </template>
          </UCard>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watchEffect } from "vue";
import type {
  JurisdictionInfo,
  JurisdictionOption,
  SuggestionResponse,
  AnalysisStepPayload,
  EditedAnalysisValues,
} from "~/types/analyzer";
import { useAnalyzerForm } from "~/composables/useAnalyzerForm";
import { useAnalysisSteps } from "~/composables/useAnalysisSteps";
import {
  buildCaseAnalyzerPayload,
  extractErrorMessage,
} from "~/utils/analyzerPayloadParser";
import JurisdictionSelectMenu from "@/components/jurisdiction-comparison/JurisdictionSelectMenu.vue";
import ConfidenceIndicator from "@/components/case-analysis/ConfidenceIndicator.vue";
import { useJurisdictions } from "@/composables/useJurisdictions";

definePageMeta({
  middleware: ["auth"],
});

useHead({ title: "AI Case Analyzer — CoLD" });

const toast = useToast();

// Jurisdictions for selector
const { data: jurisdictions } = useJurisdictions();
const selectedJurisdiction = ref<JurisdictionOption | undefined>(undefined);

// File upload state
const fileInput = ref<HTMLInputElement>();
const currentStep = ref<"upload" | "confirm" | "analyzing">("upload");
const selectedFile = ref<File | null>(null);
const isDragging = ref(false);
const isUploading = ref(false);
const error = ref<string | null>(null);

// Analysis state
const correlationId = ref<string | null>(null);
const jurisdictionInfo = ref<JurisdictionInfo | null>(null);
const analysisResults = ref<Record<string, AnalysisStepPayload>>({});

// Composables
const { analysisSteps, isAnalyzing, getFieldStatus, isFieldLoading } =
  useAnalysisSteps();

const {
  editableForm,
  isCommonLawJurisdiction,
  populateEditableForm,
  resetEditableForm,
} = useAnalyzerForm(jurisdictionInfo, analysisResults);

// UI state
const isSubmitting = ref(false);
const isSubmitted = ref(false);

// Check if field should be disabled (analyzing or submitted)
function isFieldDisabled(fieldName: keyof EditedAnalysisValues): boolean {
  if (isSubmitted.value) return true;
  return isFieldLoading(fieldName);
}

// Populate form when analysis completes
watchEffect(() => {
  if (currentStep.value === "analyzing" && !isAnalyzing.value) {
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

// Helper to update a specific step's status
function updateStepStatus(
  stepName: string,
  status: "pending" | "in_progress" | "completed" | "error",
  data?: { confidence?: string; reasoning?: string },
) {
  console.log(`updateStepStatus called: ${stepName} -> ${status}`);
  const step = analysisSteps.value.find((s) => s.name === stepName);
  console.log(`Found step:`, step);
  if (step) {
    step.status = status;
    if (data) {
      step.confidence = data.confidence || null;
      step.reasoning = data.reasoning || null;
    }
    console.log(`Updated step to:`, step);
  } else {
    console.error(`Step not found: ${stepName}`);
  }
}

// Event handlers
function handleFileDrop(e: DragEvent) {
  isDragging.value = false;
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    const file = files[0];
    if (file.type === "application/pdf") {
      selectedFile.value = file;
    } else {
      error.value = "Please select a PDF file";
    }
  }
}

function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0];
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

// Document upload and analysis
async function uploadDocument() {
  if (!selectedFile.value) return;

  isUploading.value = true;
  error.value = null;

  // Mark upload step as in progress
  updateStepStatus("document_upload", "in_progress");

  try {
    const reader = new FileReader();
    const fileContent = await new Promise<string>((resolve, reject) => {
      reader.onload = () => {
        const result = reader.result as string;
        const base64 = result.includes(",") ? result.split(",")[1] : result;
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(selectedFile.value!);
    });

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

    // Mark upload complete, start jurisdiction detection
    updateStepStatus("document_upload", "completed");
    updateStepStatus("jurisdiction_detection", "in_progress");

    const data = await $fetch<{
      correlation_id: string;
      jurisdiction: JurisdictionInfo;
    }>("/api/proxy/case-analysis/upload", {
      method: "POST",
      body: {
        file_name: selectedFile.value.name,
        blob_url,
      },
    });

    correlationId.value = data.correlation_id;
    jurisdictionInfo.value = data.jurisdiction;

    // Mark jurisdiction detection complete with confidence
    updateStepStatus("jurisdiction_detection", "completed", {
      confidence: data.jurisdiction.confidence,
      reasoning: data.jurisdiction.reasoning,
    });

    currentStep.value = "confirm";
  } catch (err: unknown) {
    console.error("Upload failed:", err);
    error.value =
      extractErrorMessage(err) ||
      "Failed to upload document. Please try again.";
    updateStepStatus("document_upload", "error");
  } finally {
    isUploading.value = false;
  }
}

function onJurisdictionSelected(jurisdiction: JurisdictionOption | undefined) {
  if (jurisdictionInfo.value && jurisdiction) {
    jurisdictionInfo.value.precise_jurisdiction = jurisdiction.Name || "";
    jurisdictionInfo.value.jurisdiction_code =
      jurisdiction.alpha3Code || jurisdictionInfo.value.jurisdiction_code;
  }
}

// Step label mapping for toast notifications
const stepLabels: Record<string, string> = {
  col_extraction: "Choice of Law Extraction",
  theme_classification: "Theme Classification",
  case_citation: "Case Citation",
  relevant_facts: "Relevant Facts",
  pil_provisions: "PIL Provisions",
  col_issue: "Choice of Law Issue",
  courts_position: "Court's Position",
  obiter_dicta: "Obiter Dicta",
  dissenting_opinions: "Dissenting Opinions",
  abstract: "Abstract",
};

async function confirmAndAnalyze(resume = false) {
  if (!correlationId.value || !jurisdictionInfo.value) return;

  isAnalyzing.value = true;
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

  try {
    const response = await fetch("/api/proxy/case-analysis/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        correlation_id: correlationId.value,
        jurisdiction: jurisdictionInfo.value,
        resume,
      }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error("No response body");
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));
            const step = analysisSteps.value.find((s) => s.name === data.step);
            if (step) {
              const prevStatus = step.status;
              step.status = data.status;
              if (data.data) {
                step.confidence = data.data.confidence || null;
                step.reasoning = data.data.reasoning || null;
                analysisResults.value[data.step] = data.data;
                populateEditableForm();
              }
              if (data.error) {
                step.error = data.error;
              }
              // Show toast when step completes
              if (data.status === "completed" && prevStatus !== "completed") {
                toast.add({
                  title: stepLabels[data.step] || data.step,
                  description: "Completed",
                  color: "teal",
                  icon: "i-heroicons-check-circle",
                  timeout: 2000,
                });
              }
            }
          } catch (e) {
            console.error("Failed to parse SSE data:", e);
          }
        }
      }
    }
  } catch (err: unknown) {
    console.error("Analysis failed:", err);
    error.value = "Analysis failed. Please try again.";
  } finally {
    isAnalyzing.value = false;
  }
}

function handleRetry(_stepName: string) {
  // Resume analysis from where it failed
  confirmAndAnalyze(true);
}

async function submitAnalyzerSuggestion() {
  if (!correlationId.value) {
    error.value = "No analysis data available";
    return;
  }
  isSubmitting.value = true;
  error.value = null;
  try {
    const suggestionPayload = buildCaseAnalyzerPayload(
      { ...editableForm },
      correlationId.value,
      jurisdictionInfo.value,
      analysisResults.value,
    );

    const response = await $fetch<SuggestionResponse>(
      "/api/proxy/suggestions/case-analyzer",
      {
        method: "POST",
        body: suggestionPayload,
        headers: {
          Source: "case-analyzer-ui",
        },
      },
    );

    isSubmitted.value = true;
    toast.add({
      title: "Submission Successful",
      description: `Suggestion #${response.id} has been submitted for review.`,
      color: "teal",
      icon: "i-heroicons-check-circle",
      timeout: 5000,
    });
  } catch (err) {
    console.error("Suggestion submission failed:", err);
    error.value =
      extractErrorMessage(err) || "Failed to submit the analyzer suggestion.";
  } finally {
    isSubmitting.value = false;
  }
}

function resetAnalysis() {
  currentStep.value = "upload";
  selectedFile.value = null;
  correlationId.value = null;
  jurisdictionInfo.value = null;
  selectedJurisdiction.value = undefined;
  analysisResults.value = {};
  resetEditableForm();
  isSubmitted.value = false;
  analysisSteps.value.forEach((step) => {
    step.status = "pending";
    step.confidence = null;
    step.reasoning = null;
    step.error = null;
  });
  error.value = null;
}
</script>
