<template>
  <div v-if="hasPdf" class="flex-shrink-0">
    <a
      :href="finalPdfUrl"
      target="_blank"
      rel="noopener noreferrer"
      class="label inline-flex items-center gap-1 text-cold-teal"
      aria-label="Download PDF for record"
      @click.stop
    >
      <UIcon name="i-material-symbols:picture-as-pdf-outline" class="h-4 w-4" />
      <span>PDF</span>
    </a>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { extractPdfUrl } from "@/utils/pdfUtils";
import { useCheckTarget } from "@/composables/useCheckTarget";

const props = defineProps<{
  recordId?: string;
  folderName?: string;
  url?: string | null;
  pdfField?: unknown;
}>();

const pdfUrl = computed(() => {
  // If a pdfField is provided, extract the URL from it
  if (props.pdfField !== undefined && props.pdfField !== null) {
    const extractedUrl = extractPdfUrl(props.pdfField);
    if (extractedUrl) {
      const urlObj = new URL(extractedUrl);
      const path = urlObj.pathname.substring(1); // Remove leading slash
      return `/api/pdf/${path}`;
    }
  }

  // If a URL is provided directly, use it (backward compatibility)
  if (props.url) {
    const urlObj = new URL(props.url);
    const path = urlObj.pathname.substring(1); // Remove leading slash
    return `/api/pdf/${path}`;
  }

  return "";
});

// Azure blob fallback URL
const azureBlobUrl = computed(() => {
  if (props.recordId && props.folderName) {
    return `https://choiceoflaw.blob.core.windows.net/${props.folderName}/${props.recordId}.pdf`;
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
