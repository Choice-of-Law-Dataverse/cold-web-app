<template>
  <UCard>
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
          v-model="localForm.caseCitation"
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
          v-model="localForm.choiceOfLawSections"
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
          v-model="localForm.themes"
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
          v-model="localForm.caseRelevantFacts"
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
          v-model="localForm.casePILProvisions"
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
          v-model="localForm.caseChoiceofLawIssue"
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
          v-model="localForm.caseCourtsPosition"
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
          v-model="localForm.caseObiterDicta"
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
          v-model="localForm.caseDissentingOpinions"
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
          v-model="localForm.caseAbstract"
          :disabled="isFieldDisabled('caseAbstract')"
          :rows="4"
        />
      </UFormGroup>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-3">
        <UButton variant="ghost" color="gray" @click="$emit('reset')">
          Start Over
        </UButton>
        <UButton
          color="primary"
          :loading="isSubmitting"
          :disabled="isAnalyzing || isSubmitted"
          @click="$emit('submit')"
        >
          {{ isSubmitted ? "Submitted" : "Submit for Review" }}
        </UButton>
      </div>
    </template>
  </UCard>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { EditedAnalysisValues } from "~/types/analyzer";
import ConfidenceIndicator from "@/components/case-analysis/ConfidenceIndicator.vue";

interface FieldStatus {
  confidence: string | null;
  reasoning: string | null;
  status: "pending" | "in_progress" | "completed" | "error";
}

const props = defineProps<{
  editableForm: EditedAnalysisValues;
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
</script>
