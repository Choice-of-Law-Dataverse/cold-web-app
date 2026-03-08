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
            leading-icon="i-material-symbols:verified-outline"
            trailing-icon="i-material-symbols:verified-outline"
            @click.prevent="isCiteOpen = true"
          >
            Cite
          </UButton>
          <UButton
            variant="outline"
            color="neutral"
            size="xs"
            leading-icon="i-material-symbols:data-object"
            trailing-icon="i-material-symbols:data-object"
            @click.prevent="exportJSON"
          >
            JSON
          </UButton>
          <UButton
            variant="outline"
            color="neutral"
            size="xs"
            leading-icon="i-material-symbols:print-outline"
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

<script setup lang="ts">
import { ref, defineAsyncComponent } from "vue";

const LazyCiteModal = defineAsyncComponent(
  () => import("@/components/ui/CiteModal.vue"),
);

const props = withDefaults(
  defineProps<{
    resultData: Record<string, unknown>;
    showSuggestEdit?: boolean;
    showOpenLink?: boolean;
    headerMode?: string;
  }>(),
  {
    showSuggestEdit: true,
    showOpenLink: true,
    headerMode: "default",
  },
);

defineEmits<{
  "open-save-modal": [];
}>();

const isCiteOpen = ref(false);

function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[<>:"/\\|?*]/g, "")
    .replace(/\s+/g, "_")
    .substring(0, 200);
}

function downloadFile(
  content: string,
  filename: string,
  mimeType: string,
): void {
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
  const title = String(
    props.resultData.title ||
      props.resultData.caseTitle ||
      props.resultData.name ||
      props.resultData.caseCitation ||
      "export",
  );
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
  gap: 0.75rem;
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
