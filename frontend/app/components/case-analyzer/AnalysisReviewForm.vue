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
      <div class="grid gap-5 md:grid-cols-2">
        <DocumentDisplay :document-name="documentName" />
        <div>
          <p class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-200">
            Jurisdiction
          </p>
          <div
            class="flex items-center gap-3 rounded-lg border border-gray-200 bg-white px-3 py-3 dark:border-gray-700 dark:bg-gray-900"
          >
            <UAvatar
              v-if="selectedJurisdiction?.avatar"
              :src="selectedJurisdiction.avatar"
              :style="{
                borderRadius: '0',
                border: '1px solid var(--color-cold-gray)',
                boxSizing: 'border-box',
                width: 'auto',
                height: '16px',
              }"
              class="flex-shrink-0"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              {{
                selectedJurisdiction?.label ||
                selectedJurisdiction?.Name ||
                "Not selected"
              }}
            </span>
          </div>
        </div>
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
      <div class="card-footer-modern no-print">
        <p class="card-footer-modern__hint">
          <UIcon name="i-heroicons-pencil-square" />
          Edit fields before submitting
        </p>
        <div class="card-footer-modern__actions">
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
            :class="isSubmitted ? 'btn-success' : 'btn-primary-gradient'"
            :loading="isSubmitting"
            :disabled="isAnalyzing || isSubmitted"
            @click="$emit('submit')"
          >
            <template #leading>
              <UIcon
                :name="
                  isSubmitted
                    ? 'i-heroicons-check-circle'
                    : 'i-heroicons-paper-airplane'
                "
                class="h-4 w-4"
              />
            </template>
            {{ isSubmitted ? "Submitted" : "Submit for Review" }}
          </UButton>
        </div>
      </div>
    </template>
  </UCard>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type {
  EditedAnalysisValues,
  JurisdictionOption,
} from "~/types/analyzer";
import type { SSEEventStatus } from "~/composables/useSSEStream";
import AnalysisFormField from "@/components/case-analyzer/AnalysisFormField.vue";
import DocumentDisplay from "@/components/case-analyzer/DocumentDisplay.vue";

interface FieldStatus {
  confidence: string | null;
  reasoning: string | null;
  status: SSEEventStatus;
}

const props = defineProps<{
  editableForm: EditedAnalysisValues;
  documentName: string;
  selectedJurisdiction: JurisdictionOption | undefined;
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
}>();

const localForm = computed({
  get: () => props.editableForm,
  set: (value) => emit("update:editableForm", value),
});

function isFieldDisabled(fieldName: keyof EditedAnalysisValues): boolean {
  if (props.isSubmitted) return true;
  const status = props.getFieldStatus(fieldName);
  return status?.status !== "completed";
}

function handlePrint() {
  window.print();
}
</script>
