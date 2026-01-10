<template>
  <UCard>
    <template #header>
      <h3 class="font-semibold">Upload Document</h3>
    </template>

    <div
      class="hover:border-primary cursor-pointer rounded-lg border-2 border-dashed border-gray-300 p-8 text-center transition-colors dark:border-gray-600"
      :class="{
        'border-primary bg-primary/5': isDragging || selectedFile,
        'pointer-events-none opacity-60': isUploading,
      }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleFileDrop"
      @click="!isUploading && fileInput?.click()"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf"
        class="hidden"
        @change="handleFileSelect"
      />

      <UIcon
        :name="
          selectedFile
            ? 'i-heroicons-document-check'
            : 'i-heroicons-arrow-up-tray'
        "
        class="mx-auto mb-3 h-10 w-10"
        :class="selectedFile ? 'text-primary' : 'text-gray-400'"
      />

      <div v-if="!selectedFile">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Drag and drop your PDF here, or
          <span class="text-primary font-medium">browse</span>
        </p>
        <p class="mt-1 text-xs text-gray-500">PDF files only</p>
      </div>

      <div v-else>
        <p class="text-sm font-medium text-gray-900 dark:text-white">
          {{ selectedFile.name }}
        </p>
        <p class="mt-1 text-xs text-gray-500">
          {{ formatFileSize(selectedFile.size) }} - Click to change
        </p>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-3">
        <UButton variant="ghost" color="gray" @click="$emit('cancel')">
          Cancel
        </UButton>
        <UButton
          color="primary"
          :disabled="!selectedFile || isUploading"
          :loading="isUploading"
          @click="$emit('upload')"
        >
          Upload and Analyze
        </UButton>
      </div>
    </template>
  </UCard>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { formatFileSize, isPdfFile } from "~/utils/fileUtils";

defineProps<{
  selectedFile: File | null;
  isUploading: boolean;
}>();

const emit = defineEmits<{
  "update:selectedFile": [file: File | null];
  upload: [];
  cancel: [];
  error: [message: string];
}>();

const fileInput = ref<HTMLInputElement>();
const isDragging = ref(false);

function handleFileDrop(e: DragEvent) {
  isDragging.value = false;
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    const file = files[0];
    if (isPdfFile(file)) {
      emit("update:selectedFile", file);
    } else {
      emit("error", "Please select a PDF file");
    }
  }
}

function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    emit("update:selectedFile", target.files[0]);
  }
}
</script>
