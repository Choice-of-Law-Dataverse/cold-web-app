<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mx-auto max-w-4xl">
      <h1 class="mb-6 text-3xl font-bold">AI Case Analyzer</h1>
      <p class="mb-8 text-gray-600 dark:text-gray-400">
        Upload a court decision PDF to automatically extract key information and
        populate the submission form.
      </p>

      <!-- Step 1: File Upload -->
      <UCard v-if="currentStep === 'upload'" class="mb-6">
        <template #header>
          <h2 class="text-xl font-semibold">Step 1: Upload Document</h2>
        </template>

        <div
          class="rounded-lg border-2 border-dashed border-gray-300 p-8 text-center dark:border-gray-700"
          :class="{ 'border-blue-500 bg-blue-50 dark:bg-blue-900': isDragging }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleFileDrop"
        >
          <UIcon
            name="i-material-symbols:cloud-upload"
            class="mb-4 text-6xl text-gray-400"
          />
          <p class="mb-4 text-lg">
            Drag and drop your PDF here, or click to select
          </p>
          <input
            ref="fileInput"
            type="file"
            accept=".pdf"
            class="hidden"
            @change="handleFileSelect"
          />
          <UButton size="lg" @click="fileInput?.click()">
            Select PDF File
          </UButton>
          <p v-if="selectedFile" class="mt-4 text-sm text-gray-600">
            Selected: {{ selectedFile.name }} ({{
              formatFileSize(selectedFile.size)
            }})
          </p>
        </div>

        <template #footer>
          <div class="flex items-center justify-between">
            <UButton variant="ghost" @click="navigateTo('/court-decision/new')">
              Cancel
            </UButton>
            <UButton
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
      <UCard v-if="currentStep === 'confirm'" class="mb-6">
        <template #header>
          <h2 class="text-xl font-semibold">Step 2: Confirm Jurisdiction</h2>
        </template>

        <div v-if="jurisdictionInfo" class="space-y-8">
          <div class="space-y-4">
            <UAlert
              :color="getConfidenceColor(jurisdictionInfo.confidence) as any"
              :title="`Detected with ${jurisdictionInfo.confidence} confidence`"
            />
            <div class="flex items-center justify-end">
              <UPopover mode="hover">
                <UButton
                  icon="i-material-symbols:info-outline"
                  variant="ghost"
                  color="gray"
                  size="sm"
                >
                  View Reasoning
                </UButton>
                <template #panel>
                  <div class="max-w-md p-4 text-sm">
                    <p class="font-semibold text-gray-900 dark:text-white">
                      Detection Reasoning:
                    </p>
                    <p class="mt-2 text-gray-700 dark:text-gray-300">
                      {{ jurisdictionInfo.reasoning }}
                    </p>
                  </div>
                </template>
              </UPopover>
            </div>
          </div>

          <UFormGroup size="lg">
            <template #label>
              <span class="label">Legal System Type</span>
            </template>
            <UInput
              v-model="jurisdictionInfo.legal_system_type"
              readonly
              class="cold-input mt-2 bg-gray-50 dark:bg-gray-800"
            />
          </UFormGroup>

          <UFormGroup size="lg">
            <template #label>
              <span class="label">Jurisdiction</span>
            </template>
            <div class="mt-2">
              <JurisdictionSelector
                :formatted-jurisdiction="{
                  Name: jurisdictionInfo.precise_jurisdiction,
                }"
                label=""
                @jurisdiction-selected="onJurisdictionSelected"
              />
            </div>
          </UFormGroup>
        </div>

        <template #footer>
          <div class="flex items-center justify-between">
            <UButton variant="ghost" @click="resetAnalysis">
              Start Over
            </UButton>
            <UButton :loading="isAnalyzing" @click="confirmAndAnalyze">
              Confirm and Continue Analysis
            </UButton>
          </div>
        </template>
      </UCard>

      <UCard v-if="showReviewForm" class="mb-6">
        <template #header>
          <div class="flex flex-col gap-4">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-xl font-semibold">
                  {{
                    isAnalyzing
                      ? "Step 3: Analyzing Document"
                      : "Step 3: Review & Submit"
                  }}
                </h2>
                <p
                  v-if="isAnalyzing"
                  class="mt-1 text-sm text-gray-500 dark:text-gray-400"
                >
                  Fields will populate as analysis completes
                </p>
                <p
                  v-else-if="draftSavedMessage"
                  class="mt-1 text-sm text-gray-500"
                >
                  Draft saved at {{ draftSavedMessage }}
                </p>
              </div>
              <UButton
                v-if="!isAnalyzing && suggestionId"
                color="gray"
                variant="ghost"
                icon="i-material-symbols:refresh"
                :loading="isLoadingExistingSuggestion"
                @click="reloadSuggestionFromServer"
              >
                Reload
              </UButton>
            </div>
            <UProgress
              v-if="isAnalyzing"
              :value="analysisProgress"
              :max="100"
              color="primary"
              size="sm"
            />
          </div>
        </template>

        <div class="space-y-6">
          <UFormGroup>
            <template #label>
              <div class="flex items-center justify-between">
                <span>Case Citation</span>
                <div class="flex items-center gap-2">
                  <UIcon
                    v-if="isFieldLoading('caseCitation')"
                    name="i-material-symbols:progress-activity"
                    class="h-4 w-4 animate-spin text-blue-500"
                  />
                  <UBadge
                    v-else-if="getFieldStatus('caseCitation')?.confidence"
                    :color="
                      getConfidenceColor(
                        getFieldStatus('caseCitation')!.confidence!,
                      )
                    "
                    size="xs"
                  >
                    {{ getFieldStatus("caseCitation")!.confidence }}
                  </UBadge>
                </div>
              </div>
            </template>
            <UInput
              v-model="editableForm.caseCitation"
              :disabled="isFieldDisabled('caseCitation')"
              class="cold-input"
            />
          </UFormGroup>

          <UFormGroup>
            <template #label>
              <div class="flex items-center justify-between">
                <span>Jurisdiction</span>
              </div>
            </template>
            <JurisdictionSelector
              :formatted-jurisdiction="{
                Name: editableForm.jurisdiction,
              }"
              label=""
              :disabled="isAnalyzing"
              @jurisdiction-selected="onReviewJurisdictionSelected"
            />
          </UFormGroup>

          <UFormGroup>
            <template #label>
              <div class="flex items-center justify-between">
                <span>Relevant Facts</span>
                <div class="flex items-center gap-2">
                  <UIcon
                    v-if="isFieldLoading('caseRelevantFacts')"
                    name="i-material-symbols:progress-activity"
                    class="h-4 w-4 animate-spin text-blue-500"
                  />
                  <UBadge
                    v-else-if="getFieldStatus('caseRelevantFacts')?.confidence"
                    :color="
                      getConfidenceColor(
                        getFieldStatus('caseRelevantFacts')!.confidence!,
                      )
                    "
                    size="xs"
                  >
                    {{ getFieldStatus("caseRelevantFacts")!.confidence }}
                  </UBadge>
                </div>
              </div>
            </template>
            <UTextarea
              v-model="editableForm.caseRelevantFacts"
              :disabled="isFieldDisabled('caseRelevantFacts')"
              :rows="4"
              class="cold-input"
            />
          </UFormGroup>

          <UFormGroup>
            <template #label>
              <div class="flex items-center justify-between">
                <span>PIL Provisions</span>
                <div class="flex items-center gap-2">
                  <UIcon
                    v-if="isFieldLoading('casePILProvisions')"
                    name="i-material-symbols:progress-activity"
                    class="h-4 w-4 animate-spin text-blue-500"
                  />
                  <UBadge
                    v-else-if="getFieldStatus('casePILProvisions')?.confidence"
                    :color="
                      getConfidenceColor(
                        getFieldStatus('casePILProvisions')!.confidence!,
                      )
                    "
                    size="xs"
                  >
                    {{ getFieldStatus("casePILProvisions")!.confidence }}
                  </UBadge>
                </div>
              </div>
            </template>
            <UTextarea
              v-model="editableForm.casePILProvisions"
              :disabled="isFieldDisabled('casePILProvisions')"
              :rows="4"
              class="cold-input"
            />
          </UFormGroup>

          <UFormGroup>
            <template #label>
              <div class="flex items-center justify-between">
                <span>Choice of Law Issue</span>
                <div class="flex items-center gap-2">
                  <UIcon
                    v-if="isFieldLoading('caseChoiceofLawIssue')"
                    name="i-material-symbols:progress-activity"
                    class="h-4 w-4 animate-spin text-blue-500"
                  />
                  <UBadge
                    v-else-if="
                      getFieldStatus('caseChoiceofLawIssue')?.confidence
                    "
                    :color="
                      getConfidenceColor(
                        getFieldStatus('caseChoiceofLawIssue')!.confidence!,
                      )
                    "
                    size="xs"
                  >
                    {{ getFieldStatus("caseChoiceofLawIssue")!.confidence }}
                  </UBadge>
                </div>
              </div>
            </template>
            <UTextarea
              v-model="editableForm.caseChoiceofLawIssue"
              :disabled="isFieldDisabled('caseChoiceofLawIssue')"
              :rows="4"
              class="cold-input"
            />
          </UFormGroup>

          <UFormGroup>
            <template #label>
              <div class="flex items-center justify-between">
                <span>Court's Position</span>
                <div class="flex items-center gap-2">
                  <UIcon
                    v-if="isFieldLoading('caseCourtsPosition')"
                    name="i-material-symbols:progress-activity"
                    class="h-4 w-4 animate-spin text-blue-500"
                  />
                  <UBadge
                    v-else-if="getFieldStatus('caseCourtsPosition')?.confidence"
                    :color="
                      getConfidenceColor(
                        getFieldStatus('caseCourtsPosition')!.confidence!,
                      )
                    "
                    size="xs"
                  >
                    {{ getFieldStatus("caseCourtsPosition")!.confidence }}
                  </UBadge>
                </div>
              </div>
            </template>
            <UTextarea
              v-model="editableForm.caseCourtsPosition"
              :disabled="isFieldDisabled('caseCourtsPosition')"
              :rows="4"
              class="cold-input"
            />
          </UFormGroup>

          <UFormGroup v-if="isCommonLawJurisdiction">
            <template #label>
              <div class="flex items-center justify-between">
                <span>Obiter Dicta</span>
                <div class="flex items-center gap-2">
                  <UIcon
                    v-if="isFieldLoading('caseObiterDicta')"
                    name="i-material-symbols:progress-activity"
                    class="h-4 w-4 animate-spin text-blue-500"
                  />
                  <UBadge
                    v-else-if="getFieldStatus('caseObiterDicta')?.confidence"
                    :color="
                      getConfidenceColor(
                        getFieldStatus('caseObiterDicta')!.confidence!,
                      )
                    "
                    size="xs"
                  >
                    {{ getFieldStatus("caseObiterDicta")!.confidence }}
                  </UBadge>
                </div>
              </div>
            </template>
            <UTextarea
              v-model="editableForm.caseObiterDicta"
              :disabled="isFieldDisabled('caseObiterDicta')"
              :rows="4"
              class="cold-input"
            />
          </UFormGroup>

          <UFormGroup v-if="isCommonLawJurisdiction">
            <template #label>
              <div class="flex items-center justify-between">
                <span>Dissenting Opinions</span>
                <div class="flex items-center gap-2">
                  <UIcon
                    v-if="isFieldLoading('caseDissentingOpinions')"
                    name="i-material-symbols:progress-activity"
                    class="h-4 w-4 animate-spin text-blue-500"
                  />
                  <UBadge
                    v-else-if="
                      getFieldStatus('caseDissentingOpinions')?.confidence
                    "
                    :color="
                      getConfidenceColor(
                        getFieldStatus('caseDissentingOpinions')!.confidence!,
                      )
                    "
                    size="xs"
                  >
                    {{ getFieldStatus("caseDissentingOpinions")!.confidence }}
                  </UBadge>
                </div>
              </div>
            </template>
            <UTextarea
              v-model="editableForm.caseDissentingOpinions"
              :disabled="isFieldDisabled('caseDissentingOpinions')"
              :rows="4"
              class="cold-input"
            />
          </UFormGroup>

          <UFormGroup>
            <template #label>
              <div class="flex items-center justify-between">
                <span>Abstract</span>
                <div class="flex items-center gap-2">
                  <UIcon
                    v-if="isFieldLoading('caseAbstract')"
                    name="i-material-symbols:progress-activity"
                    class="h-4 w-4 animate-spin text-blue-500"
                  />
                  <UBadge
                    v-else-if="getFieldStatus('caseAbstract')?.confidence"
                    :color="
                      getConfidenceColor(
                        getFieldStatus('caseAbstract')!.confidence!,
                      )
                    "
                    size="xs"
                  >
                    {{ getFieldStatus("caseAbstract")!.confidence }}
                  </UBadge>
                </div>
              </div>
            </template>
            <UTextarea
              v-model="editableForm.caseAbstract"
              :disabled="isFieldDisabled('caseAbstract')"
              :rows="4"
              class="cold-input"
            />
          </UFormGroup>
        </div>

        <template #footer>
          <div class="flex items-center justify-between">
            <UButton color="gray" variant="outline" @click="resetAnalysis">
              Start Over
            </UButton>
            <div class="flex gap-2">
              <UButton
                v-if="!isAnalyzing"
                color="gray"
                :loading="isSavingDraft"
                @click="saveEditedDraft"
              >
                Save Draft
              </UButton>
              <UButton
                color="primary"
                :loading="isSubmitting"
                :disabled="isAnalyzing"
                @click="submitAnalyzerSuggestion"
              >
                Submit for Review
              </UButton>
            </div>
          </div>
        </template>
      </UCard>

      <UAlert
        v-if="submissionMessage"
        color="green"
        icon="i-material-symbols:check-circle"
        :title="submissionMessage"
        class="mb-6"
      />

      <!-- Error Display -->
      <UAlert
        v-if="error"
        color="red"
        icon="i-material-symbols:error"
        :title="error"
        class="mb-6"
        @close="error = null"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, watchEffect, onMounted } from "vue";
import type {
  JurisdictionInfo,
  EditedAnalysisValues,
  SuggestionResponse,
  AnalysisStepPayload,
  CaseAnalyzerSuggestionRecord,
} from "~/types/analyzer";
import { useAnalyzerForm } from "~/composables/useAnalyzerForm";
import { useAnalysisSteps } from "~/composables/useAnalysisSteps";
import { useAnalyzerStorage } from "~/composables/useAnalyzerStorage";
import {
  buildCaseAnalyzerPayload,
  extractErrorMessage,
} from "~/utils/analyzerPayloadParser";
import JurisdictionSelector from "@/components/ui/JurisdictionSelector.vue";

definePageMeta({
  middleware: ["auth"],
});

useHead({ title: "AI Case Analyzer — CoLD" });

const router = useRouter();
const route = useRoute();

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
const {
  analysisSteps,
  isAnalyzing,
  getFieldStatus,
  isFieldLoading,
  isFieldDisabled,
  hydrateAnalysisStepsFromResults,
  markStepsCompleteWithoutResults,
  getConfidenceColor,
} = useAnalysisSteps();

const {
  editableForm,
  isCommonLawJurisdiction,
  populateEditableForm,
  resetEditableForm,
} = useAnalyzerForm(jurisdictionInfo, analysisResults);

const {
  suggestionId,
  lastFetchedSuggestionId,
  isLoadingExistingSuggestion,
  draftSavedMessage,
  storeAnalysisResults,
  parseSuggestionIdParam,
  applySuggestionRecord,
} = useAnalyzerStorage(
  correlationId,
  jurisdictionInfo,
  analysisResults,
  editableForm,
  hydrateAnalysisStepsFromResults,
  markStepsCompleteWithoutResults,
);

// UI state
const isSavingDraft = ref(false);
const isSubmitting = ref(false);
const submissionMessage = ref<string | null>(null);

const showReviewForm = computed(() => {
  return currentStep.value === "analyzing";
});

const analysisProgress = computed(() => {
  if (!analysisSteps.value.length) return 0;
  const completed = analysisSteps.value.filter(
    (step) => step.status === "completed",
  ).length;
  return Math.round((completed / analysisSteps.value.length) * 100);
});

// Lifecycle hooks
watchEffect(() => {
  if (
    showReviewForm.value &&
    suggestionId.value === null &&
    !isAnalyzing.value
  ) {
    populateEditableForm();
  }
});

onMounted(() => {
  const initialSuggestionId = parseSuggestionIdParam(route.query.suggestionId);
  if (initialSuggestionId !== null) {
    fetchCaseAnalyzerSuggestion(initialSuggestionId, {
      syncQuery: false,
      silent: true,
    });
  }
});

if (import.meta.client) {
  watch(
    () => route.query.suggestionId,
    (newValue) => {
      const parsed = parseSuggestionIdParam(newValue);
      if (parsed === null) {
        suggestionId.value = null;
        return;
      }
      if (parsed === lastFetchedSuggestionId.value) {
        suggestionId.value = parsed;
        return;
      }
      fetchCaseAnalyzerSuggestion(parsed, { syncQuery: false, silent: true });
    },
  );
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
    currentStep.value = "confirm";
  } catch (err: unknown) {
    console.error("Upload failed:", err);
    error.value =
      extractErrorMessage(err) ||
      "Failed to upload document. Please try again.";
  } finally {
    isUploading.value = false;
  }
}

function onJurisdictionSelected(jurisdiction: {
  Name?: string;
  alpha3Code?: string;
}) {
  if (jurisdictionInfo.value && jurisdiction) {
    jurisdictionInfo.value.precise_jurisdiction = jurisdiction.Name || "";
    jurisdictionInfo.value.jurisdiction_code =
      jurisdiction.alpha3Code || jurisdictionInfo.value.jurisdiction_code;
  }
}

function onReviewJurisdictionSelected(jurisdiction: { Name?: string }) {
  if (jurisdiction?.Name) {
    editableForm.jurisdiction = jurisdiction.Name;
  }
}

async function confirmAndAnalyze() {
  if (!correlationId.value || !jurisdictionInfo.value) return;

  isAnalyzing.value = true;
  currentStep.value = "analyzing";
  error.value = null;

  try {
    const response = await fetch("/api/proxy/case-analysis/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        correlation_id: correlationId.value,
        jurisdiction: jurisdictionInfo.value,
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
            }
          } catch (e) {
            console.error("Failed to parse SSE data:", e);
          }
        }
      }
    }

    storeAnalysisResults();
  } catch (err: unknown) {
    console.error("Analysis failed:", err);
    error.value = "Analysis failed. Please try again.";
  } finally {
    isAnalyzing.value = false;
  }
}

async function saveEditedDraft() {
  if (!showReviewForm.value) return;
  isSavingDraft.value = true;
  try {
    storeAnalysisResults();
    draftSavedMessage.value = new Date().toLocaleTimeString();
  } finally {
    isSavingDraft.value = false;
  }
}

async function submitAnalyzerSuggestion() {
  if (!correlationId.value) {
    error.value = "No analysis data available";
    return;
  }
  isSubmitting.value = true;
  error.value = null;
  try {
    const editedPayload: EditedAnalysisValues = { ...editableForm };
    storeAnalysisResults(editedPayload);
    const suggestionPayload = buildCaseAnalyzerPayload(
      editedPayload,
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

    lastFetchedSuggestionId.value = response.id;
    updateSuggestionId(response.id);
    await fetchCaseAnalyzerSuggestion(response.id, { syncQuery: false });

    submissionMessage.value = `Thanks! Suggestion #${response.id} has been stored.`;
  } catch (err) {
    console.error("Suggestion submission failed:", err);
    error.value =
      extractErrorMessage(err) || "Failed to submit the analyzer suggestion.";
  } finally {
    isSubmitting.value = false;
  }
}

async function fetchCaseAnalyzerSuggestion(
  id: number,
  options: { syncQuery?: boolean; silent?: boolean } = {},
) {
  if (!Number.isFinite(id)) {
    return;
  }

  isLoadingExistingSuggestion.value = true;

  try {
    const record = await $fetch<CaseAnalyzerSuggestionRecord>(
      `/api/proxy/suggestions/case-analyzer/${id}`,
    );
    lastFetchedSuggestionId.value = id;
    updateSuggestionId(id, { syncQuery: options.syncQuery !== false });

    if (record.payload) {
      applySuggestionRecord(record.payload);
      currentStep.value = "analyzing";
    }

    if (!options.silent) {
      submissionMessage.value = `Loaded suggestion #${id} from database.`;
    }
  } catch (err) {
    console.error("Failed to load suggestion:", err);
    error.value =
      extractErrorMessage(err) || `Unable to load suggestion #${id}.`;
  } finally {
    isLoadingExistingSuggestion.value = false;
  }
}

function updateSuggestionId(
  id: number | null,
  options: { syncQuery?: boolean } = {},
) {
  suggestionId.value = id;

  if (options.syncQuery === false) {
    return;
  }

  const currentQuery = { ...route.query } as Record<string, string | string[]>;
  const existingId = parseSuggestionIdParam(currentQuery.suggestionId);

  if (id === null) {
    if (currentQuery.suggestionId === undefined) {
      return;
    }
    delete currentQuery.suggestionId;
    void router.replace({ path: route.path, query: currentQuery });
    return;
  }

  if (existingId === id) {
    return;
  }

  currentQuery.suggestionId = String(id);
  void router.replace({ path: route.path, query: currentQuery });
}

async function reloadSuggestionFromServer() {
  if (!suggestionId.value) {
    return;
  }
  await fetchCaseAnalyzerSuggestion(suggestionId.value);
}

function resetAnalysis() {
  currentStep.value = "upload";
  selectedFile.value = null;
  correlationId.value = null;
  jurisdictionInfo.value = null;
  analysisResults.value = {};
  lastFetchedSuggestionId.value = null;
  updateSuggestionId(null);
  resetEditableForm();
  submissionMessage.value = null;
  analysisSteps.value.forEach((step) => {
    step.status = "pending";
    step.confidence = null;
    step.reasoning = null;
    step.error = null;
  });
  error.value = null;
}
</script>

<style scoped>
.cold-input {
  background-color: #ffffff;
}

:global(.dark) .cold-input {
  background-color: #111827;
}
</style>
