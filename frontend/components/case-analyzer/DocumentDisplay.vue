<template>
  <div>
    <p class="mb-2 text-sm font-medium text-gray-700 dark:text-gray-200">
      Document
    </p>
    <div
      class="flex items-center gap-3 rounded-lg border border-gray-200 bg-white px-4 py-3 dark:border-gray-700 dark:bg-gray-900"
    >
      <UIcon
        name="i-heroicons-document-text"
        class="h-5 w-5 flex-shrink-0 text-red-500"
      />
      <span class="text-sm text-gray-700 dark:text-gray-300">
        {{ documentName }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  documentName: string;
}>();
</script>
