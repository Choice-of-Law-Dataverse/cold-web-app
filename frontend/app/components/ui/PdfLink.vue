<template>
  <div v-if="hasPdf" class="flex-shrink-0">
    <UButton
      :to="finalPdfUrl"
      target="_blank"
      variant="ghost"
      color="primary"
      size="xs"
      icon="i-material-symbols:picture-as-pdf-outline"
      trailing-icon="i-material-symbols:picture-as-pdf-outline"
      aria-label="Download PDF for record"
      @click.stop
    >
      PDF
    </UButton>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import {
  getPdfProxyUrl,
  extractStoragePath,
  buildProxyUrl,
} from "@/utils/storage";
import { useCheckTarget } from "@/composables/useCheckTarget";
import { BLOB_STORAGE_BASE_URL } from "@/config/assets";

const props = defineProps<{
  recordId?: string;
  folderName?: string;
  url?: string | null;
  pdfField?: unknown;
}>();

const pdfUrl = computed(() => {
  if (props.pdfField !== undefined && props.pdfField !== null) {
    return getPdfProxyUrl(props.pdfField) || "";
  }

  if (props.url) {
    const storagePath = extractStoragePath(props.url);
    return storagePath ? buildProxyUrl(storagePath) : "";
  }

  return "";
});

const azureBlobUrl = computed(() => {
  if (props.recordId && props.folderName) {
    return `${BLOB_STORAGE_BASE_URL}/${props.folderName}/${props.recordId}.pdf`;
  }
  return "";
});

// Only check Azure blob when we don't have a pdfUrl
const checkUrl = computed(() => (pdfUrl.value ? "" : azureBlobUrl.value));
const { data: azureBlobExists } = useCheckTarget(checkUrl);

const hasPdf = computed(() => {
  // If we have a pdfUrl from pdfField or url, show the PDF link immediately
  if (pdfUrl.value) {
    return true;
  }

  // If using Azure blob fallback, only show if it exists
  if (azureBlobUrl.value) {
    return azureBlobExists.value === true;
  }

  return false;
});

const finalPdfUrl = computed(() => pdfUrl.value || azureBlobUrl.value);
</script>
