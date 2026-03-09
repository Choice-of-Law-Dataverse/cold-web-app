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
                :label="sourceLinkLabel"
                :open-access="!!data.openAccessUrl"
              />
            </template>
          </TitleWithActions>
        </DetailRow>
      </section>
    </template>

    <template #abstractNote>
      <section>
        <DetailRow label="BibTeX Citation">
          <div class="flex flex-col gap-3">
            <pre
              class="overflow-x-auto rounded-md bg-gray-50 p-4 font-mono text-xs dark:bg-gray-800"
              >{{ bibtexContent }}</pre
            >
            <div class="flex gap-3">
              <UButton
                variant="outline"
                color="neutral"
                size="xs"
                icon="i-material-symbols:content-copy-outline"
                @click="copyBibTeX"
              >
                Copy
              </UButton>
              <UButton
                variant="outline"
                color="neutral"
                size="xs"
                icon="i-material-symbols:download-2-outline"
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
import type { LiteratureDetailResponse } from "@/types/entities/literature";
import { generateBibTeX, sanitizeFilename, downloadFile } from "@/utils/bibtex";

const props = defineProps<{
  data: Record<string, unknown>;
}>();

const sourceUrl = computed(() => {
  if (props.data.openAccessUrl) return String(props.data.openAccessUrl);
  return String(props.data.url || "");
});

const sourceLinkLabel = computed(() =>
  props.data.openAccessUrl ? "Open Access Link" : "Link",
);

const bibtexContent = computed(() =>
  generateBibTeX(props.data as unknown as LiteratureDetailResponse),
);

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
  const rawTitle = String(props.data.title || "literature");
  const filename = `${sanitizeFilename(rawTitle)}.bib`;
  downloadFile(bibtexContent.value, filename, "application/x-bibtex");
}
</script>
