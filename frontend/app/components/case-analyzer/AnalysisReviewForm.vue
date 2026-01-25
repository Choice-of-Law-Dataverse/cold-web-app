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

      <UFormGroup>
        <template #label>
          Choice of Law Sections
          <ConfidenceIndicator
            :is-loading="isFieldLoading('choiceOfLawSections')"
            :field-status="getFieldStatus('choiceOfLawSections')"
          />
        </template>
        <UTextarea
          v-model="localForm.choiceOfLawSections"
          :disabled="isFieldDisabled('choiceOfLawSections')"
          :rows="6"
          class="print:hidden"
        />
        <div class="print-field-value">
          {{ localForm.choiceOfLawSections }}
        </div>
      </UFormGroup>

      <UFormGroup>
        <template #label>
          Themes
          <ConfidenceIndicator
            :is-loading="isFieldLoading('themes')"
            :field-status="getFieldStatus('themes')"
          />
        </template>
        <UTextarea
          v-model="localForm.themes"
          :disabled="isFieldDisabled('themes')"
          :rows="1"
          class="print:hidden"
        />
        <div class="print-field-value">
          {{ localForm.themes }}
        </div>
      </UFormGroup>

      <UFormGroup>
        <template #label>
          Case Citation
          <ConfidenceIndicator
            :is-loading="isFieldLoading('caseCitation')"
            :field-status="getFieldStatus('caseCitation')"
          />
        </template>
        <UInput
          v-model="localForm.caseCitation"
          :disabled="isFieldDisabled('caseCitation')"
          :rows="2"
          class="print:hidden"
        />
        <div class="print-field-value">
          {{ localForm.caseCitation }}
        </div>
      </UFormGroup>

      <UFormGroup>
        <template #label>
          Relevant Facts
          <ConfidenceIndicator
            :is-loading="isFieldLoading('caseRelevantFacts')"
            :field-status="getFieldStatus('caseRelevantFacts')"
          />
        </template>
        <UTextarea
          v-model="localForm.caseRelevantFacts"
          :disabled="isFieldDisabled('caseRelevantFacts')"
          :rows="6"
          class="print:hidden"
        />
        <div class="print-field-value">
          {{ localForm.caseRelevantFacts }}
        </div>
      </UFormGroup>

      <UFormGroup>
        <template #label>
          PIL Provisions
          <ConfidenceIndicator
            :is-loading="isFieldLoading('casePILProvisions')"
            :field-status="getFieldStatus('casePILProvisions')"
          />
        </template>
        <UTextarea
          v-model="localForm.casePILProvisions"
          :disabled="isFieldDisabled('casePILProvisions')"
          :rows="2"
          class="print:hidden"
        />
        <div class="print-field-value">
          {{ localForm.casePILProvisions }}
        </div>
      </UFormGroup>

      <UFormGroup>
        <template #label>
          Choice of Law Issue
          <ConfidenceIndicator
            :is-loading="isFieldLoading('caseChoiceofLawIssue')"
            :field-status="getFieldStatus('caseChoiceofLawIssue')"
          />
        </template>
        <UTextarea
          v-model="localForm.caseChoiceofLawIssue"
          :disabled="isFieldDisabled('caseChoiceofLawIssue')"
          :rows="6"
          class="print:hidden"
        />
        <div class="print-field-value">
          {{ localForm.caseChoiceofLawIssue }}
        </div>
      </UFormGroup>

      <UFormGroup>
        <template #label>
          Court's Position
          <ConfidenceIndicator
            :is-loading="isFieldLoading('caseCourtsPosition')"
            :field-status="getFieldStatus('caseCourtsPosition')"
          />
        </template>
        <UTextarea
          v-model="localForm.caseCourtsPosition"
          :disabled="isFieldDisabled('caseCourtsPosition')"
          :rows="6"
          class="print:hidden"
        />
        <div class="print-field-value">
          {{ localForm.caseCourtsPosition }}
        </div>
      </UFormGroup>

      <UFormGroup v-if="isCommonLawJurisdiction">
        <template #label>
          Obiter Dicta
          <ConfidenceIndicator
            :is-loading="isFieldLoading('caseObiterDicta')"
            :field-status="getFieldStatus('caseObiterDicta')"
          />
        </template>
        <UTextarea
          v-model="localForm.caseObiterDicta"
          :disabled="isFieldDisabled('caseObiterDicta')"
          :rows="3"
          class="print:hidden"
        />
        <div class="print-field-value">
          {{ localForm.caseObiterDicta }}
        </div>
      </UFormGroup>

      <UFormGroup v-if="isCommonLawJurisdiction">
        <template #label>
          Dissenting Opinions
          <ConfidenceIndicator
            :is-loading="isFieldLoading('caseDissentingOpinions')"
            :field-status="getFieldStatus('caseDissentingOpinions')"
          />
        </template>
        <UTextarea
          v-model="localForm.caseDissentingOpinions"
          :disabled="isFieldDisabled('caseDissentingOpinions')"
          :rows="3"
          class="print:hidden"
        />
        <div class="print-field-value">
          {{ localForm.caseDissentingOpinions }}
        </div>
      </UFormGroup>

      <UFormGroup>
        <template #label>
          Abstract
          <ConfidenceIndicator
            :is-loading="isFieldLoading('caseAbstract')"
            :field-status="getFieldStatus('caseAbstract')"
          />
        </template>
        <UTextarea
          v-model="localForm.caseAbstract"
          :disabled="isFieldDisabled('caseAbstract')"
          :rows="6"
          class="print:hidden"
        />
        <div class="print-field-value">
          {{ localForm.caseAbstract }}
        </div>
      </UFormGroup>
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
import ConfidenceIndicator from "@/components/case-analyzer/ConfidenceIndicator.vue";
import DocumentDisplay from "@/components/case-analyzer/DocumentDisplay.vue";

interface FieldStatus {
  confidence: string | null;
  reasoning: string | null;
  status: "pending" | "in_progress" | "completed" | "error";
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
  return props.isFieldLoading(fieldName);
}

function handlePrint() {
  window.print();
}
</script>
