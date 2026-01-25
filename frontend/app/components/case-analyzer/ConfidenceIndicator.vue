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
  <span class="no-print inline-flex items-center gap-1">
    <!-- Loading spinner -->
    <UIcon
      v-if="isLoading"
      name="i-material-symbols:progress-activity"
      class="text-cold-teal h-3.5 w-3.5 animate-spin"
    />
    <!-- Confidence indicator with optional reasoning popover -->
    <template v-else-if="fieldStatus?.confidence">
      <UPopover v-if="fieldStatus.reasoning" mode="hover">
        <span
          class="text-cold-teal/70 hover:text-cold-teal cursor-help text-xs"
        >
          {{ fieldStatus.confidence }}
        </span>
        <template #content>
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
      <span v-else class="text-cold-teal/70 text-xs">
        {{ fieldStatus.confidence }}
      </span>
    </template>
  </span>
</template>
