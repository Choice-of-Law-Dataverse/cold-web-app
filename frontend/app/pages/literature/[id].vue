<template>
  <div>
    <BaseDetailLayout
      table="Literature"
      :loading="loading"
      :error="error"
      :data="literature || {}"
      :labels="literatureLabels"
      :tooltips="literatureTooltips"
      :show-suggest-edit="true"
    >
      <!-- Title with PDF and Source Link -->
      <template #title="{ value }">
        <section v-if="value" class="section-gap">
          <DetailRow :label="literatureLabels['Title']">
            <div class="flex items-start justify-between gap-4">
              <div class="result-value-small flex-1">{{ value }}</div>
              <div class="flex flex-shrink-0 items-center gap-3">
                <PdfLink
                  :pdf-field="literature?.['Official Source (PDF)']"
                  :record-id="id"
                  folder-name="literatures"
                />
                <SourceExternalLink
                  :source-url="sourceUrl"
                  :label="sourceLinkLabel"
                  :open-access="!!literature?.['Open Access URL']"
                />
              </div>
            </div>
          </DetailRow>
        </section>
      </template>

      <template #publication-title="{ value }">
        <section v-if="value" class="section-gap">
          <DetailRow :label="literatureLabels['Publication Title']">
            <span class="result-value-small">{{ value }}</span>
          </DetailRow>
        </section>
      </template>

      <template #publisher="{ value }">
        <section v-if="value" class="section-gap">
          <DetailRow
            :label="literatureLabels['Publisher']"
            :tooltip="literatureTooltips['Publisher']"
          >
            <span class="result-value-small">{{ value }}</span>
          </DetailRow>
        </section>
      </template>

      <!-- BibTeX Export Section -->
      <template #abstract-note>
        <section class="section-gap">
          <DetailRow label="BibTeX Citation">
            <div class="flex flex-col gap-3">
              <pre
                class="overflow-x-auto rounded-md bg-gray-50 p-4 font-mono text-xs dark:bg-gray-800"
                >{{ bibtexContent }}</pre
              >
              <div class="flex gap-3">
                <button class="action-button" @click="copyBibTeX">
                  <UIcon name="i-material-symbols:content-copy-outline" />
                  <span>Copy</span>
                </button>
                <button class="action-button" @click="exportBibTeX">
                  <UIcon name="i-material-symbols:download-2-outline" />
                  <span>Download</span>
                </button>
              </div>
            </div>
          </DetailRow>
        </section>
      </template>

      <template #footer>
        <LastModified :date="literature?.['Last Modified'] as string" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[literature?.Title as string]"
      fallback="Literature"
    />

    <EntityFeedback
      entity-type="literature"
      :entity-id="id"
      :entity-title="literature?.Title as string"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useLiterature } from "@/composables/useRecordDetails";
import DetailRow from "@/components/ui/DetailRow.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { generateBibTeX, sanitizeFilename, downloadFile } from "@/utils/bibtex";
import { literatureLabels } from "@/config/labels";
import { literatureTooltips } from "@/config/tooltips";

const route = useRoute();

// Capture the ID once at setup to prevent flash during page transitions
const id = ref(route.params.id as string);

const { data: literature, isLoading: loading, error } = useLiterature(id);

// Source URL logic
const sourceUrl = computed(() => {
  if (!literature.value) return "";
  if (literature.value["Open Access URL"]) {
    return literature.value["Open Access URL"] as string;
  }
  return (literature.value["Url"] || "") as string;
});

const sourceLinkLabel = computed(() => {
  if (literature.value?.["Open Access URL"]) {
    return "Open Access Link";
  }
  return "Link";
});

// BibTeX computed property and export function
const bibtexContent = computed(() => {
  if (!literature.value) return "";
  return generateBibTeX(literature.value);
});

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
  } catch (error) {
    toast.add({
      title: "Copy failed",
      description: `Could not copy to clipboard: ${error instanceof Error ? error.message : String(error)}`,
      icon: "i-material-symbols:error-outline",
      color: "error",
      duration: 3000,
    });
  }
}

function exportBibTeX() {
  const bibtex = bibtexContent.value;
  const rawTitle = (literature.value?.Title || "literature") as string;
  const filename = `${sanitizeFilename(rawTitle)}.bib`;
  downloadFile(bibtex, filename, "application/x-bibtex");
}
</script>
