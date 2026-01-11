<template>
  <UCard class="overflow-hidden">
    <template #header>
      <div class="flex items-center gap-3">
        <div>
          <h3 class="font-semibold text-gray-900 dark:text-white">
            Upload Document
          </h3>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            PDF format supported
          </p>
        </div>
      </div>
    </template>

    <div
      class="group relative cursor-pointer overflow-hidden rounded-2xl border-2 border-dashed transition-all duration-300"
      :class="[
        isDragging
          ? 'scale-[1.02] border-cold-purple bg-cold-purple/10'
          : selectedFile
            ? 'border-cold-teal bg-cold-teal/5'
            : 'border-gray-200 bg-gradient-to-br from-gray-50 to-white hover:border-cold-purple/50 hover:from-cold-purple/5 hover:to-cold-teal/5 dark:border-gray-700 dark:from-gray-800 dark:to-gray-900 dark:hover:border-cold-purple/50',
        isUploading ? 'pointer-events-none opacity-60' : '',
      ]"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleFileDrop"
      @click="!isUploading && fileInput?.click()"
    >
      <!-- Decorative background elements -->
      <div
        class="pointer-events-none absolute inset-0 opacity-30 transition-opacity duration-300 group-hover:opacity-50"
      >
        <div
          class="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-gradient-to-br from-cold-purple/20 to-transparent"
        />
        <div
          class="absolute -bottom-8 -left-8 h-32 w-32 rounded-full bg-gradient-to-tr from-cold-teal/20 to-transparent"
        />
      </div>

      <input
        ref="fileInput"
        type="file"
        accept=".pdf"
        class="hidden"
        @change="handleFileSelect"
      />

      <div class="relative px-8 py-12">
        <!-- Upload illustration -->
        <div class="mb-6 flex justify-center">
          <div class="relative">
            <!-- Main icon container -->
            <div
              class="relative flex h-20 w-20 items-center justify-center rounded-2xl transition-all duration-300"
              :class="[
                selectedFile
                  ? 'bg-gradient-to-br from-cold-teal to-cold-green shadow-lg shadow-cold-teal/25'
                  : 'bg-gradient-to-br from-cold-purple/10 to-cold-teal/10 group-hover:from-cold-purple/20 group-hover:to-cold-teal/20',
                isDragging ? 'scale-110' : '',
              ]"
            >
              <UIcon
                :name="
                  selectedFile
                    ? 'i-heroicons-document-check'
                    : 'i-heroicons-document-arrow-up'
                "
                class="h-10 w-10 transition-all duration-300"
                :class="
                  selectedFile
                    ? 'text-white'
                    : 'text-cold-purple group-hover:scale-110'
                "
              />
            </div>

            <!-- Animated sparkles for AI effect -->
            <div
              v-if="!selectedFile"
              class="absolute -right-1 -top-1 flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-cold-purple to-cold-teal opacity-0 transition-all duration-300 group-hover:opacity-100"
            >
              <svg
                class="h-3 w-3 text-white"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path
                  d="M12 2L13.09 8.26L19 9L13.09 9.74L12 16L10.91 9.74L5 9L10.91 8.26L12 2Z"
                />
              </svg>
            </div>
            <div
              v-if="!selectedFile"
              class="absolute -bottom-1 -left-1 flex h-4 w-4 items-center justify-center rounded-full bg-gradient-to-br from-cold-teal to-cold-green opacity-0 transition-all delay-100 duration-300 group-hover:opacity-100"
            >
              <svg
                class="h-2 w-2 text-white"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path
                  d="M12 2L13.09 8.26L19 9L13.09 9.74L12 16L10.91 9.74L5 9L10.91 8.26L12 2Z"
                />
              </svg>
            </div>

            <!-- Success checkmark animation -->
            <div
              v-if="selectedFile"
              class="absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full border-2 border-white bg-cold-green shadow-lg dark:border-gray-800"
            >
              <UIcon name="i-heroicons-check" class="h-4 w-4 text-white" />
            </div>
          </div>
        </div>

        <!-- Text content -->
        <div v-if="!selectedFile" class="text-center">
          <p class="text-base font-medium text-gray-700 dark:text-gray-200">
            Drag and drop your court decision
          </p>
          <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
            or
            <span
              class="font-semibold text-cold-purple transition-colors group-hover:text-cold-teal"
              >click to browse</span
            >
          </p>
          <div
            class="mt-4 inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1.5 dark:bg-gray-800"
          >
            <UIcon name="i-heroicons-document" class="h-4 w-4 text-gray-400" />
            <span class="text-xs font-medium text-gray-500 dark:text-gray-400"
              >PDF files only • Max 50MB</span
            >
          </div>
        </div>

        <div v-else class="text-center">
          <p
            class="truncate text-base font-semibold text-gray-900 dark:text-white"
          >
            {{ selectedFile.name }}
          </p>
          <p class="mt-1 text-sm text-cold-teal">
            {{ formatFileSize(selectedFile.size) }}
          </p>
          <button
            type="button"
            class="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-gray-500 transition-colors hover:text-cold-purple dark:text-gray-400"
            @click.stop="!isUploading && fileInput?.click()"
          >
            <UIcon name="i-heroicons-arrow-path" class="h-4 w-4" />
            Choose different file
          </button>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="card-footer-modern">
        <p class="card-footer-modern__hint">
          <UIcon name="i-heroicons-lock-closed" />
          Securely processed with AI
        </p>
        <div class="card-footer-modern__actions">
          <UButton variant="ghost" color="gray" @click="$emit('cancel')">
            Cancel
          </UButton>
          <UButton
            class="btn-primary-gradient"
            :disabled="!selectedFile || isUploading"
            :loading="isUploading"
            @click="$emit('upload')"
          >
            <template #leading>
              <UIcon name="i-heroicons-sparkles" class="h-4 w-4" />
            </template>
            Analyze with AI
          </UButton>
        </div>
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
