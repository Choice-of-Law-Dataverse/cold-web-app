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
        <div class="icon-action" @click.prevent.stop="navigateToDetail">
          <UIcon
            name="i-material-symbols:arrow-forward"
            class="icon-action__icon"
          />
        </div>
      </template>
    </template>
  </div>
  <LazyCiteModal v-model="isCiteOpen" />
</template>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent } from "vue";
import { getBasePathForCard } from "@/config/entityRegistry";

const LazyCiteModal = defineAsyncComponent(
  () => import("@/components/ui/CiteModal.vue"),
);

const props = withDefaults(
  defineProps<{
    resultData: Record<string, unknown>;
    cardType?: string;
    showSuggestEdit?: boolean;
    showOpenLink?: boolean;
    headerMode?: string;
  }>(),
  {
    cardType: "",
    showSuggestEdit: true,
    showOpenLink: true,
    headerMode: "default",
  },
);

const detailPath = computed(() => {
  if (!props.cardType) return undefined;
  const basePath = getBasePathForCard(props.cardType);
  const id = props.resultData.id;
  if (basePath && id) return `${basePath}/${id}`;
  return undefined;
});

function navigateToDetail() {
  if (detailPath.value) navigateTo(detailPath.value);
}

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

.icon-action {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  cursor: pointer;
  border-radius: 0.25rem;
}

.icon-action__icon {
  font-size: 1.5rem;
  color: var(--color-cold-purple);
  transition: transform 0.2s ease;
}

.icon-action:hover .icon-action__icon,
.icon-action:focus-visible .icon-action__icon {
  transform: scale(1.2);
}
</style>
