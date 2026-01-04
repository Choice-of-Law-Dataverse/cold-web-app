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
            <UButton
              variant="ghost"
              @click="$router.push('/court-decision/new')"
            >
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

        <div v-if="jurisdictionInfo" class="space-y-4">
          <UAlert
            :icon="getConfidenceIcon(jurisdictionInfo.confidence)"
            :color="getConfidenceColor(jurisdictionInfo.confidence) as any"
            :title="`Detected with ${jurisdictionInfo.confidence} confidence`"
          />

          <UFormGroup label="Legal System Type">
            <UInput
              v-model="jurisdictionInfo.legal_system_type"
              readonly
              class="bg-gray-50 dark:bg-gray-800"
            />
          </UFormGroup>

          <UFormGroup label="Jurisdiction">
            <UInput
              v-model="jurisdictionInfo.precise_jurisdiction"
              class="cold-input"
            />
          </UFormGroup>

          <UFormGroup label="Country Code">
            <UInput
              v-model="jurisdictionInfo.jurisdiction_code"
              class="cold-input"
            />
          </UFormGroup>

          <UFormGroup label="Reasoning">
            <UTextarea
              v-model="jurisdictionInfo.reasoning"
              :rows="3"
              readonly
              class="bg-gray-50 dark:bg-gray-800"
            />
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

      <!-- Step 3: Analysis Progress -->
      <UCard v-if="currentStep === 'analyzing'" class="mb-6">
        <template #header>
          <h2 class="text-xl font-semibold">Step 3: Analysis in Progress</h2>
        </template>

        <div class="space-y-4">
          <div
            v-for="step in analysisSteps"
            :key="step.name"
            class="rounded-lg border p-4"
            :class="{
              'border-blue-500 bg-blue-50 dark:bg-blue-900':
                step.status === 'in_progress',
              'border-green-500 bg-green-50 dark:bg-green-900':
                step.status === 'completed',
              'border-red-500 bg-red-50 dark:bg-red-900':
                step.status === 'error',
              'border-gray-300 dark:border-gray-700': step.status === 'pending',
            }"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <UIcon
                  v-if="step.status === 'pending'"
                  name="i-material-symbols:pending"
                  class="text-2xl text-gray-400"
                />
                <UIcon
                  v-if="step.status === 'in_progress'"
                  name="i-material-symbols:autorenew"
                  class="animate-spin text-2xl text-blue-500"
                />
                <UIcon
                  v-if="step.status === 'completed'"
                  name="i-material-symbols:check-circle"
                  class="text-2xl text-green-500"
                />
                <UIcon
                  v-if="step.status === 'error'"
                  name="i-material-symbols:error"
                  class="text-2xl text-red-500"
                />
                <span class="font-medium">{{ step.label }}</span>
              </div>
              <span
                v-if="step.confidence"
                class="rounded px-2 py-1 text-sm"
                :class="{
                  'bg-green-200 text-green-800': step.confidence === 'high',
                  'bg-yellow-200 text-yellow-800': step.confidence === 'medium',
                  'bg-red-200 text-red-800': step.confidence === 'low',
                }"
              >
                {{ step.confidence }} confidence
              </span>
            </div>
            <div v-if="step.error" class="mt-2 text-sm text-red-600">
              Error: {{ step.error }}
            </div>
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end">
            <UButton v-if="analysisComplete" @click="goToForm">
              Go to Form
            </UButton>
          </div>
        </template>
      </UCard>

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
import { ref, computed } from "vue";
import { useRouter } from "#imports";

definePageMeta({
  middleware: ["auth"],
});

useHead({ title: "AI Case Analyzer — CoLD" });

const router = useRouter();

const fileInput = ref<HTMLInputElement>();
const currentStep = ref<"upload" | "confirm" | "analyzing">("upload");
const selectedFile = ref<File | null>(null);
const isDragging = ref(false);
const isUploading = ref(false);
const isAnalyzing = ref(false);
const error = ref<string | null>(null);

interface JurisdictionInfo {
  legal_system_type: string;
  precise_jurisdiction: string;
  jurisdiction_code: string;
  confidence: string;
  reasoning: string;
}

const correlationId = ref<string | null>(null);
const jurisdictionInfo = ref<JurisdictionInfo | null>(null);
const analysisResults = ref<Record<string, unknown>>({});

const analysisSteps = ref([
  {
    name: "col_extraction",
    label: "Choice of Law Extraction",
    status: "pending",
    confidence: null,
    error: null,
  },
  {
    name: "theme_classification",
    label: "Theme Classification",
    status: "pending",
    confidence: null,
    error: null,
  },
  {
    name: "case_citation",
    label: "Case Citation",
    status: "pending",
    confidence: null,
    error: null,
  },
  {
    name: "abstract",
    label: "Abstract Generation",
    status: "pending",
    confidence: null,
    error: null,
  },
  {
    name: "relevant_facts",
    label: "Relevant Facts",
    status: "pending",
    confidence: null,
    error: null,
  },
  {
    name: "pil_provisions",
    label: "PIL Provisions",
    status: "pending",
    confidence: null,
    error: null,
  },
  {
    name: "col_issue",
    label: "Choice of Law Issue",
    status: "pending",
    confidence: null,
    error: null,
  },
  {
    name: "courts_position",
    label: "Court's Position",
    status: "pending",
    confidence: null,
    error: null,
  },
]);

const analysisComplete = computed(() => {
  return analysisSteps.value.every(
    (step) => step.status === "completed" || step.status === "error",
  );
});

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
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB";
  return (bytes / (1024 * 1024)).toFixed(2) + " MB";
}

async function uploadDocument() {
  if (!selectedFile.value) return;

  isUploading.value = true;
  error.value = null;

  try {
    const reader = new FileReader();
    const fileContent = await new Promise<string>((resolve, reject) => {
      reader.onload = () => {
        const result = reader.result as string;
        // Strip the data URL prefix (e.g., "data:application/pdf;base64,")
        const base64 = result.includes(",") ? result.split(",")[1] : result;
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(selectedFile.value!);
    });

    // For local dev: send directly to backend
    // For production: upload to Azure first, then send blob URL
    const useDirectUpload = true; // TODO: make this environment-based

    let blob_url: string;

    if (useDirectUpload) {
      // Direct upload - backend will handle the PDF bytes
      blob_url = `data:application/pdf;base64,${fileContent}`;
    } else {
      // Upload to Azure Blob Storage first
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

    // Send to backend for processing
    const data = await $fetch<{
      correlation_id: string;
      jurisdiction: JurisdictionInfo;
    }>("/api/proxy/case-analysis/upload", {
      method: "POST",
      body: {
        file_name: selectedFile.value.name,
        blob_url: blob_url,
      },
    });

    correlationId.value = data.correlation_id;
    jurisdictionInfo.value = data.jurisdiction;
    currentStep.value = "confirm";
  } catch (err: unknown) {
    console.error("Upload failed:", err);
    if (err && typeof err === "object") {
      const error = err as Record<string, unknown>;
      console.error("Error data:", error.data);
      console.error("Error message:", error.message);
      console.error("Error statusCode:", error.statusCode);
    }
    const errorMessage =
      err &&
      typeof err === "object" &&
      "data" in err &&
      err.data &&
      typeof err.data === "object" &&
      "detail" in err.data
        ? String(err.data.detail)
        : "Failed to upload document. Please try again.";
    error.value = errorMessage;
  } finally {
    isUploading.value = false;
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
          const data = JSON.parse(line.slice(6));

          if (data.done) {
            break;
          }

          const stepIndex = analysisSteps.value.findIndex(
            (s) => s.name === data.step,
          );
          if (stepIndex !== -1) {
            analysisSteps.value[stepIndex].status = data.status;
            if (data.data) {
              analysisSteps.value[stepIndex].confidence = data.data.confidence;
              analysisResults.value[data.step] = data.data;
            }
            if (data.error) {
              analysisSteps.value[stepIndex].error = data.error;
            }
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

function storeAnalysisResults() {
  if (typeof window !== "undefined") {
    sessionStorage.setItem(
      "caseAnalysisResults",
      JSON.stringify({
        correlationId: correlationId.value,
        jurisdiction: jurisdictionInfo.value,
        results: analysisResults.value,
      }),
    );
  }
}

function goToForm() {
  router.push("/court-decision/new?fromAnalysis=true");
}

function resetAnalysis() {
  currentStep.value = "upload";
  selectedFile.value = null;
  correlationId.value = null;
  jurisdictionInfo.value = null;
  analysisResults.value = {};
  analysisSteps.value.forEach((step) => {
    step.status = "pending";
    step.confidence = null;
    step.error = null;
  });
  error.value = null;
}

function getConfidenceIcon(confidence: string): string {
  switch (confidence) {
    case "high":
      return "i-material-symbols:check-circle";
    case "medium":
      return "i-material-symbols:warning";
    case "low":
      return "i-material-symbols:error";
    default:
      return "i-material-symbols:info";
  }
}

function getConfidenceColor(
  confidence: string,
): "green" | "yellow" | "red" | "gray" {
  switch (confidence) {
    case "high":
      return "green";
    case "medium":
      return "yellow";
    case "low":
      return "red";
    default:
      return "gray";
  }
}
</script>

<style scoped>
.cold-input {
  @apply bg-white dark:bg-gray-900;
}
</style>
