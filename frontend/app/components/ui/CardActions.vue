<template>
  <div class="ml-auto flex items-center justify-self-end">
    <template v-if="headerMode === 'new'">
      <UButton size="xs" @click="$emit('open-save-modal')">
        Submit your data
      </UButton>
    </template>
    <template v-else>
      <template v-if="showSuggestEdit">
        <div class="actions-container hidden flex-row items-center sm:flex">
          <UButton
            variant="outline"
            color="neutral"
            size="xs"
            trailing-icon="i-material-symbols:verified-outline"
            @click.prevent="isCiteOpen = true"
          >
            Cite
          </UButton>
          <UButton
            variant="outline"
            color="neutral"
            size="xs"
            trailing-icon="i-material-symbols:data-object"
            @click.prevent="exportJSON"
          >
            JSON
          </UButton>
          <UButton
            variant="outline"
            color="neutral"
            size="xs"
            trailing-icon="i-material-symbols:print-outline"
            @click.prevent="printPage"
          >
            Print
          </UButton>
        </div>
      </template>
      <template v-else-if="showOpenLink">
        <div class="arrow-container">
          <UIcon name="i-material-symbols:arrow-forward" class="arrow-icon" />
        </div>
      </template>
    </template>
  </div>
  <LazyCiteModal v-model="isCiteOpen" />
</template>

<script setup>
import { ref, defineAsyncComponent } from "vue";

const LazyCiteModal = defineAsyncComponent(
  () => import("@/components/ui/CiteModal.vue"),
);

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
  showSuggestEdit: {
    type: Boolean,
    default: true,
  },
  showOpenLink: {
    type: Boolean,
    default: true,
  },
  headerMode: {
    type: String,
    default: "default",
  },
});

defineEmits(["open-save-modal"]);

const isCiteOpen = ref(false);

function sanitizeFilename(filename) {
  return filename
    .replace(/[<>:"/\\|?*]/g, "")
    .replace(/\s+/g, "_")
    .substring(0, 200);
}

function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function exportJSON() {
  const json = JSON.stringify(props.resultData, null, 2);
  const title =
    props.resultData.Title ||
    props.resultData["Case Title"] ||
    props.resultData.Name ||
    props.resultData["Case Citation"] ||
    "export";
  const filename = `${sanitizeFilename(title)}.json`;
  downloadFile(json, filename, "application/json");
}

function printPage() {
  window.print();
}
</script>

<style scoped>
.actions-container {
  align-items: center;
}

.actions-container :deep(button) {
  margin-right: 1.25rem;
  transition: margin-right 0.2s ease;
}

.actions-container :deep(button:last-child) {
  margin-right: 0;
}

.actions-container :deep(button:hover) {
  margin-right: 0.125rem;
}

.actions-container :deep(button:last-child:hover) {
  margin-right: -1.125rem;
}

.arrow-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
}

.arrow-icon {
  font-size: 1.5rem;
  color: var(--color-cold-purple);
  transition: transform 0.3s ease;
}
</style>
