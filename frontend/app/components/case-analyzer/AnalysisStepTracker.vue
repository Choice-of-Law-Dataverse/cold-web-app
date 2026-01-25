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
      <div class="card-header-modern">
        <div class="card-header-modern__text">
          <h3>Progress</h3>
          <p>Analysis steps</p>
        </div>
      </div>
    </template>

    <div class="flex flex-row flex-wrap gap-3 lg:flex-col">
      <div
        v-for="step in visibleSteps"
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
            'text-sm',
            step.status === 'completed'
              ? 'text-gray-700 dark:text-gray-300'
              : step.status === 'in_progress'
                ? 'text-cold-teal font-medium'
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
          color="error"
          variant="ghost"
          icon="i-heroicons-arrow-path"
          @click="emit('retry', step.name)"
        />
      </div>
    </div>
  </UCard>
</template>
