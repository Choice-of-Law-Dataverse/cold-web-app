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
  recordId: string;
  folderName: string;
}>();

const pdfUrl = computed(() => {
  if (!props.recordId) return "";
  return `https://choiceoflaw.blob.core.windows.net/${props.folderName}/${props.recordId}.pdf`;
});

const { data: hasPdf } = useCheckTarget(toRef(() => pdfUrl.value));
</script>
