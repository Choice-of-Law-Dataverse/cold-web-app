<template>
  <UCard>
    <template #header>
      <div class="flex items-center gap-3">
        <div>
          <h3 class="font-semibold text-gray-900 dark:text-white">
            {{ isAnalyzing ? "Extracting Data..." : "Review & Submit" }}
          </h3>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            {{
              isAnalyzing
                ? "AI is analyzing your document"
                : "Verify and edit extracted data"
            }}
          </p>
        </div>
      </div>
    </template>

    <div class="space-y-5">
      <DocumentDisplay :document-name="documentName" />

      <div class="grid gap-5 md:grid-cols-2">
        <UFormField label="Jurisdiction">
          <div v-if="jurisdictionsLoading" class="text-sm text-gray-500">
            Loading jurisdictions...
          </div>
          <div v-else-if="jurisdictionsError" class="text-sm text-gray-500">
            Failed to load jurisdictions
          </div>
          <JurisdictionSelectMenu
            v-else
            :model-value="selectedJurisdiction"
            :jurisdictions="jurisdictions || []"
            placeholder="Select jurisdiction"
            :disabled="isAnalyzing || isSubmitted"
            @update:model-value="handleJurisdictionChange"
          />
        </UFormField>
        <UFormField label="Legal System Type">
          <USelect
            :model-value="legalSystemType"
            :items="legalSystemOptions"
            placeholder="Select legal system"
            size="xl"
            class="w-full"
            :disabled="isAnalyzing || isSubmitted"
            @update:model-value="
              (value) => handleLegalSystemChange(value as string)
            "
          />
        </UFormField>
      </div>

      <AnalysisFormField
        label="Choice of Law Sections"
        :model-value="localForm.choiceOfLawSections"
        :field-status="getFieldStatus('choiceOfLawSections')"
        :is-field-loading="isFieldLoading('choiceOfLawSections')"
        :disabled="isFieldDisabled('choiceOfLawSections')"
        :rows="9"
        @update:model-value="localForm.choiceOfLawSections = $event"
      />

      <AnalysisFormField
        label="Themes"
        :model-value="localForm.themes"
        :field-status="getFieldStatus('themes')"
        :is-field-loading="isFieldLoading('themes')"
        :disabled="isFieldDisabled('themes')"
        :rows="1"
        @update:model-value="localForm.themes = $event"
      />

      <AnalysisFormField
        label="Case Citation"
        :model-value="localForm.caseCitation"
        :field-status="getFieldStatus('caseCitation')"
        :is-field-loading="isFieldLoading('caseCitation')"
        :disabled="isFieldDisabled('caseCitation')"
        :rows="2"
        @update:model-value="localForm.caseCitation = $event"
      />

      <AnalysisFormField
        label="Relevant Facts"
        :model-value="localForm.caseRelevantFacts"
        :field-status="getFieldStatus('caseRelevantFacts')"
        :is-field-loading="isFieldLoading('caseRelevantFacts')"
        :disabled="isFieldDisabled('caseRelevantFacts')"
        :rows="9"
        @update:model-value="localForm.caseRelevantFacts = $event"
      />

      <AnalysisFormField
        label="PIL Provisions"
        :model-value="localForm.casePILProvisions"
        :field-status="getFieldStatus('casePILProvisions')"
        :is-field-loading="isFieldLoading('casePILProvisions')"
        :disabled="isFieldDisabled('casePILProvisions')"
        :rows="2"
        @update:model-value="localForm.casePILProvisions = $event"
      />

      <AnalysisFormField
        label="Choice of Law Issue"
        :model-value="localForm.caseChoiceofLawIssue"
        :field-status="getFieldStatus('caseChoiceofLawIssue')"
        :is-field-loading="isFieldLoading('caseChoiceofLawIssue')"
        :disabled="isFieldDisabled('caseChoiceofLawIssue')"
        :rows="6"
        @update:model-value="localForm.caseChoiceofLawIssue = $event"
      />

      <AnalysisFormField
        label="Court's Position"
        :model-value="localForm.caseCourtsPosition"
        :field-status="getFieldStatus('caseCourtsPosition')"
        :is-field-loading="isFieldLoading('caseCourtsPosition')"
        :disabled="isFieldDisabled('caseCourtsPosition')"
        :rows="9"
        @update:model-value="localForm.caseCourtsPosition = $event"
      />

      <AnalysisFormField
        v-if="isCommonLawJurisdiction"
        label="Obiter Dicta"
        :model-value="localForm.caseObiterDicta"
        :field-status="getFieldStatus('caseObiterDicta')"
        :is-field-loading="isFieldLoading('caseObiterDicta')"
        :disabled="isFieldDisabled('caseObiterDicta')"
        :rows="6"
        @update:model-value="localForm.caseObiterDicta = $event"
      />

      <AnalysisFormField
        v-if="isCommonLawJurisdiction"
        label="Dissenting Opinions"
        :model-value="localForm.caseDissentingOpinions"
        :field-status="getFieldStatus('caseDissentingOpinions')"
        :is-field-loading="isFieldLoading('caseDissentingOpinions')"
        :disabled="isFieldDisabled('caseDissentingOpinions')"
        :rows="6"
        @update:model-value="localForm.caseDissentingOpinions = $event"
      />

      <AnalysisFormField
        label="Abstract"
        :model-value="localForm.caseAbstract"
        :field-status="getFieldStatus('caseAbstract')"
        :is-field-loading="isFieldLoading('caseAbstract')"
        :disabled="isFieldDisabled('caseAbstract')"
        :rows="9"
        @update:model-value="localForm.caseAbstract = $event"
      />
    </div>

    <template #footer>
      <CardFooterModern class="no-print">
        <template #hint>
          <UIcon name="i-heroicons-pencil-square" />
          Edit fields before submitting
        </template>
        <UButton variant="ghost" color="neutral" @click="$emit('reset')">
          Start Over
        </UButton>
        <UButton
          variant="ghost"
          color="neutral"
          :disabled="isAnalyzing"
          @click="handlePrint"
        >
          <template #leading>
            <UIcon name="i-heroicons-printer" class="h-4 w-4" />
          </template>
          Print
        </UButton>
        <UButton
          v-if="isSubmitted"
          color="success"
          variant="solid"
          :loading="isSubmitting"
          :disabled="isAnalyzing || isSubmitted"
          @click="$emit('submit')"
        >
          <template #leading>
            <UIcon name="i-heroicons-check-circle" class="h-4 w-4" />
          </template>
          Submitted
        </UButton>
        <AppButtonGradient
          v-else
          :loading="isSubmitting"
          :disabled="isAnalyzing"
          @click="$emit('submit')"
        >
          <template #leading>
            <UIcon name="i-heroicons-paper-airplane" class="h-4 w-4" />
          </template>
          Submit for Review
        </AppButtonGradient>
      </CardFooterModern>
    </template>

    <UModal
      v-model:open="showConfirmModal"
      :dismissible="false"
      title="Re-run analysis?"
    >
      <template #content>
        <div class="p-6 text-center">
          <h2 class="mb-4 text-lg font-bold">Re-run analysis?</h2>
          <p class="mb-6">
            Changing the jurisdiction will discard the current extraction
            results and re-run the entire analysis from the beginning. Any edits
            you've made will be lost.
          </p>
          <div class="flex justify-center gap-4">
            <UButton color="neutral" variant="outline" @click="cancelChange">
              Cancel
            </UButton>
            <UButton color="primary" @click="confirmChange">
              Re-run Analysis
            </UButton>
          </div>
        </div>
      </template>
    </UModal>
  </UCard>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type {
  EditedAnalysisValues,
  JurisdictionOption,
} from "~/types/analyzer";
import CardFooterModern from "@/components/ui/CardFooterModern.vue";
import AppButtonGradient from "@/components/ui/AppButtonGradient.vue";
import type { SSEEventStatus } from "~/utils/sseStream";
import AnalysisFormField from "@/components/case-analyzer/AnalysisFormField.vue";
import DocumentDisplay from "@/components/case-analyzer/DocumentDisplay.vue";
import JurisdictionSelectMenu from "@/components/jurisdiction/JurisdictionSelectMenu.vue";
import { useJurisdictions } from "@/composables/useJurisdictions";

interface FieldStatus {
  confidence: string | null;
  reasoning: string | null;
  status: SSEEventStatus;
}

const props = defineProps<{
  editableForm: EditedAnalysisValues;
  documentName: string;
  selectedJurisdiction: JurisdictionOption | undefined;
  legalSystemType: string;
  isCommonLawJurisdiction: boolean;
  isAnalyzing: boolean;
  isSubmitting: boolean;
  isSubmitted: boolean;
  getFieldStatus: (
    fieldName: keyof EditedAnalysisValues,
  ) => FieldStatus | null | undefined;
  isFieldLoading: (fieldName: keyof EditedAnalysisValues) => boolean;
}>();

const emit = defineEmits<{
  "update:editableForm": [form: EditedAnalysisValues];
  submit: [];
  reset: [];
  "re-analyze": [
    legalSystemType: string,
    jurisdiction: JurisdictionOption | undefined,
  ];
}>();

const {
  data: jurisdictions,
  isLoading: jurisdictionsLoading,
  error: jurisdictionsError,
} = useJurisdictions();

const legalSystemOptionsBase = [
  "Civil-law jurisdiction",
  "Common-law jurisdiction",
  "No court decision",
];

const legalSystemOptions = computed(() => {
  const options = [...legalSystemOptionsBase];
  if (props.legalSystemType && !options.includes(props.legalSystemType)) {
    options.push(props.legalSystemType);
  }
  return options;
});

const showConfirmModal = ref(false);
const pendingLegalSystem = ref<string | null>(null);
const pendingJurisdiction = ref<JurisdictionOption | undefined>(undefined);

const localForm = computed({
  get: () => props.editableForm,
  set: (value) => emit("update:editableForm", value),
});

function isFieldDisabled(fieldName: keyof EditedAnalysisValues): boolean {
  if (props.isSubmitted) return true;
  const status = props.getFieldStatus(fieldName);
  return status?.status !== "completed";
}

function handleLegalSystemChange(value: string | undefined) {
  if (!value || value === props.legalSystemType) return;
  pendingLegalSystem.value = value;
  pendingJurisdiction.value = props.selectedJurisdiction;
  showConfirmModal.value = true;
}

function handleJurisdictionChange(
  jurisdiction: JurisdictionOption | undefined,
) {
  if (
    !jurisdiction ||
    jurisdiction.coldId === props.selectedJurisdiction?.coldId
  ) {
    return;
  }
  pendingLegalSystem.value = props.legalSystemType;
  pendingJurisdiction.value = jurisdiction;
  showConfirmModal.value = true;
}

function confirmChange() {
  emit(
    "re-analyze",
    pendingLegalSystem.value ?? props.legalSystemType,
    pendingJurisdiction.value,
  );
  showConfirmModal.value = false;
  pendingLegalSystem.value = null;
  pendingJurisdiction.value = undefined;
}

function cancelChange() {
  showConfirmModal.value = false;
  pendingLegalSystem.value = null;
  pendingJurisdiction.value = undefined;
}

function handlePrint() {
  window.print();
}
</script>
