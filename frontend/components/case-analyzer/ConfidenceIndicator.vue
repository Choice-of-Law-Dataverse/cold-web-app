<script setup lang="ts">
defineProps<{
  isLoading: boolean;
  fieldStatus:
    | { confidence: string | null; reasoning: string | null }
    | null
    | undefined;
}>();
</script>

<template>
  <span class="inline-flex items-center gap-1">
    <!-- Loading spinner -->
    <UIcon
      v-if="isLoading"
      name="i-material-symbols:progress-activity"
      class="h-3.5 w-3.5 animate-spin text-cold-teal"
    />
    <!-- Confidence indicator with optional reasoning popover -->
    <template v-else-if="fieldStatus?.confidence">
      <UPopover v-if="fieldStatus.reasoning" mode="hover">
        <span
          class="cursor-help text-xs text-cold-teal/70 hover:text-cold-teal"
        >
          {{ fieldStatus.confidence }}
        </span>
        <template #panel>
          <div class="max-w-xs p-3 text-xs">
            <p class="font-medium text-gray-700 dark:text-gray-300">
              Reasoning
            </p>
            <p class="mt-1 text-gray-600 dark:text-gray-400">
              {{ fieldStatus.reasoning }}
            </p>
          </div>
        </template>
      </UPopover>
      <span v-else class="text-xs text-cold-teal/70">
        {{ fieldStatus.confidence }}
      </span>
    </template>
  </span>
</template>
