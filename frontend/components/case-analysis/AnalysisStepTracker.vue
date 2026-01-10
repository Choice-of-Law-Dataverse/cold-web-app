<script setup lang="ts">
import type { AnalysisStep } from "~/types/analyzer";

const props = defineProps<{
  steps: AnalysisStep[];
  isCommonLaw: boolean;
  currentPhase?: "upload" | "confirm" | "analyzing" | "review";
}>();

const emit = defineEmits<{
  retry: [stepName: string];
}>();

// Group steps by phase
const phases = computed(() => [
  {
    name: "Document Processing",
    steps: ["document_upload", "jurisdiction_detection"],
  },
  {
    name: "Content Extraction",
    steps: [
      "col_extraction",
      "theme_classification",
      "case_citation",
      "relevant_facts",
      "pil_provisions",
      "col_issue",
      "courts_position",
      ...(props.isCommonLaw ? ["obiter_dicta", "dissenting_opinions"] : []),
    ],
  },
  {
    name: "Summary",
    steps: ["abstract"],
  },
]);

const visibleSteps = computed(() => {
  return props.steps.filter((step) => {
    // Always hide common-law specific steps for civil law
    if (!props.isCommonLaw) {
      if (["obiter_dicta", "dissenting_opinions"].includes(step.name)) {
        return false;
      }
    }
    return true;
  });
});

function getStepsForPhase(phaseSteps: string[]) {
  return visibleSteps.value.filter((step) => phaseSteps.includes(step.name));
}

function getStatusIcon(status: string): string {
  switch (status) {
    case "completed":
      return "i-material-symbols-check-circle";
    case "in_progress":
      return "i-material-symbols-sync";
    case "error":
      return "i-material-symbols-error";
    default:
      return "i-material-symbols-schedule";
  }
}

function getStatusColor(status: string): string {
  switch (status) {
    case "completed":
      return "text-green-500 dark:text-green-400";
    case "in_progress":
      return "text-cold-teal";
    case "error":
      return "text-red-500";
    default:
      return "text-gray-300 dark:text-gray-600";
  }
}
</script>

<template>
  <UCard>
    <template #header>
      <h3 class="text-sm font-semibold">Progress</h3>
    </template>

    <div class="space-y-5">
      <div v-for="phase in phases" :key="phase.name">
        <p
          class="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400"
        >
          {{ phase.name }}
        </p>
        <div class="space-y-2">
          <div
            v-for="step in getStepsForPhase(phase.steps)"
            :key="step.name"
            class="flex items-center gap-2"
          >
            <UIcon
              :name="getStatusIcon(step.status)"
              :class="[
                'h-4 w-4 flex-shrink-0',
                getStatusColor(step.status),
                step.status === 'in_progress' ? 'animate-spin' : '',
              ]"
            />
            <span
              :class="[
                'flex-1 text-sm',
                step.status === 'completed'
                  ? 'text-gray-700 dark:text-gray-300'
                  : step.status === 'in_progress'
                    ? 'font-medium text-cold-teal'
                    : step.status === 'error'
                      ? 'text-red-600 dark:text-red-400'
                      : 'text-gray-400 dark:text-gray-500',
              ]"
            >
              {{ step.label }}
            </span>
            <UButton
              v-if="step.status === 'error'"
              size="xs"
              color="red"
              variant="ghost"
              icon="i-heroicons-arrow-path"
              @click="emit('retry', step.name)"
            />
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>
