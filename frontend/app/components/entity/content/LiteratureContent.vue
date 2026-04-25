<template>
  <EntityContent base-path="/literature" :data="data">
    <template #title="{ value, label }">
      <section v-if="value">
        <DetailRow :label="label">
          <TitleWithActions>
            {{ value }}
            <template #actions>
              <PdfLink
                :pdf-field="undefined"
                :record-id="String(data.coldId || '')"
                folder-name="literatures"
              />
              <SourceExternalLink
                :source-url="sourceUrl"
                :open-access="!!data.openAccessUrl"
              />
            </template>
          </TitleWithActions>
        </DetailRow>
      </section>
    </template>

    <template #author="{ value, label }">
      <section v-if="value && value !== data.editor">
        <DetailRow :label="label">
          <p class="result-value-small whitespace-pre-line">{{ value }}</p>
        </DetailRow>
      </section>
    </template>

    <template #itemType="{ value, label }">
      <section v-if="value">
        <DetailRow :label="label">
          <p class="result-value-small">{{ formatItemType(String(value)) }}</p>
        </DetailRow>
      </section>
    </template>

    <template #after-fields>
      <section>
        <DetailRow label="BibTeX Citation">
          <div class="flex flex-col gap-3">
            <pre
              class="overflow-x-auto rounded-md bg-gray-50 p-4 font-mono text-xs"
              >{{ bibtexContent }}</pre
            >
            <div class="flex gap-3">
              <UButton
                variant="outline"
                color="neutral"
                size="xs"
                leading-icon="i-material-symbols:content-copy-outline"
                trailing-icon="i-material-symbols:content-copy-outline"
                @click="copyBibTeX"
              >
                Copy
              </UButton>
              <UButton
                variant="outline"
                color="neutral"
                size="xs"
                leading-icon="i-material-symbols:download-2-outline"
                trailing-icon="i-material-symbols:download-2-outline"
                @click="exportBibTeX"
              >
                Download
              </UButton>
            </div>
          </div>
        </DetailRow>
      </section>
    </template>
  </EntityContent>
</template>

<script setup lang="ts">
import { computed } from "vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import TitleWithActions from "@/components/ui/TitleWithActions.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import type { Literature } from "@/types/entities/literature";
import { generateBibTeX, sanitizeFilename, downloadFile } from "@/utils/bibtex";
import { camelCaseToLabel } from "@/utils/camelCaseToLabel";

function formatItemType(value: string): string {
  return camelCaseToLabel(value);
}

const props = defineProps<{
  data: Literature;
}>();

const sourceUrl = computed(() => {
  if (props.data.openAccessUrl) return String(props.data.openAccessUrl);
  return String(props.data.url || "");
});

const bibtexContent = computed(() => generateBibTeX(props.data));

const toast = useToast();

async function copyBibTeX() {
  try {
    await navigator.clipboard.writeText(bibtexContent.value);
    toast.add({
      title: "Copied!",
      description: "BibTeX citation copied to clipboard",
      icon: "i-material-symbols:check-circle",
      color: "success",
      duration: 3000,
    });
  } catch (err) {
    toast.add({
      title: "Copy failed",
      description: `Could not copy to clipboard: ${err instanceof Error ? err.message : String(err)}`,
      icon: "i-material-symbols:error-outline",
      color: "error",
      duration: 3000,
    });
  }
}

function exportBibTeX() {
  const rawTitle = props.data.title || "literature";
  const filename = `${sanitizeFilename(rawTitle)}.bib`;
  downloadFile(bibtexContent.value, filename, "application/x-bibtex");
}
</script>
