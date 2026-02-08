<template>
  <UFormField>
    <template #label>{{ label }}</template>
    <template #hint>
      <ConfidenceIndicator
        :is-loading="isFieldLoading"
        :field-status="fieldStatus"
      />
    </template>
    <UTextarea
      :model-value="modelValue"
      :disabled="disabled"
      :rows="rows"
      class="w-full print:hidden"
      @update:model-value="$emit('update:modelValue', $event)"
    />
    <div class="print-field-value">
      {{ modelValue }}
    </div>
  </UFormField>
</template>

<script setup lang="ts">
import ConfidenceIndicator from "@/components/case-analyzer/ConfidenceIndicator.vue";

defineProps<{
  label: string;
  modelValue: string;
  fieldStatus:
    | { confidence: string | null; reasoning: string | null; status: string }
    | null
    | undefined;
  isFieldLoading: boolean;
  disabled: boolean;
  rows?: number;
}>();

defineEmits<{
  "update:modelValue": [value: string];
}>();
</script>
