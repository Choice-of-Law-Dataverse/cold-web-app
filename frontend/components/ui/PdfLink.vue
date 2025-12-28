<template>
  <div v-if="hasPdf" class="flex-shrink-0">
    <a
      :href="pdfUrl"
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
import { computed, toRef } from "vue";
import { useCheckTarget } from "@/composables/useCheckTarget";

const props = defineProps<{
  recordId?: string;
  folderName?: string;
  url?: string;
}>();

const pdfUrl = computed(() => {
  // If a URL is provided directly, use it
  if (props.url) {
    // If it's an R2 storage URL, proxy it for authentication
    if (props.url.includes('r2.cloudflarestorage.com')) {
      // Extract the path after the domain
      const urlObj = new URL(props.url);
      const path = urlObj.pathname.substring(1); // Remove leading slash
      return `/api/r2-proxy/${path}`;
    }
    return props.url;
  }
  
  // Fall back to constructing Azure blob URL if recordId and folderName are provided
  if (!props.recordId || !props.folderName) return "";
  return `https://choiceoflaw.blob.core.windows.net/${props.folderName}/${props.recordId}.pdf`;
});

const { data: hasPdf } = useCheckTarget(toRef(() => pdfUrl.value));
</script>
