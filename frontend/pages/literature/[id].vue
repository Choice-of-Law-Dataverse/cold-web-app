<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="literature || {}"
      :key-label-pairs="computedKeyLabelPairs"
      :value-class-map="valueClassMap"
      :show-suggest-edit="true"
      source-table="Literature"
    >
      <!-- Title with PDF and Source Link -->
      <template #title="{ value }">
        <section v-if="value" class="section-gap">
          <DetailRow
            :label="keyLabelLookup.get('Title')?.label || 'Title'"
            :tooltip="keyLabelLookup.get('Title')?.tooltip"
          >
            <div class="flex items-start justify-between gap-4">
              <div :class="valueClassMap.Title" class="flex-1">{{ value }}</div>
              <div class="flex flex-shrink-0 items-center gap-3">
                <PdfLink :url="pdfUrl" :record-id="id" folder-name="literatures" />
                <SourceExternalLink
                  :source-url="sourceUrl"
                  :label="sourceLinkLabel"
                />
              </div>
            </div>
          </DetailRow>
        </section>
      </template>

      <template #publication-title="{ value }">
        <section v-if="value" class="section-gap">
          <DetailRow
            :label="
              keyLabelLookup.get('Publication Title')?.label || 'Publication'
            "
            :tooltip="keyLabelLookup.get('Publication Title')?.tooltip"
          >
            <span class="result-value-small">{{ value }}</span>
          </DetailRow>
        </section>
      </template>

      <template #publisher="{ value }">
        <section v-if="value" class="section-gap">
          <DetailRow
            :label="keyLabelLookup.get('Publisher')?.label || 'Publisher'"
            :tooltip="keyLabelLookup.get('Publisher')?.tooltip"
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
              <button
                class="label flex w-fit items-center gap-1 text-cold-teal"
                @click="exportBibTeX"
              >
                <UIcon
                  name="i-material-symbols:download-2-outline"
                  class="h-4 w-4"
                />
                <span>Download</span>
              </button>
            </div>
          </DetailRow>
        </section>
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[literature?.Title as string]"
      fallback="Literature"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import DetailRow from "@/components/ui/DetailRow.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { literatureConfig } from "@/config/pageConfigs";
import { extractPdfUrl } from "@/utils/pdfUtils";
import type { TableName } from "@/types/api";
import { generateBibTeX, sanitizeFilename, downloadFile } from "@/utils/bibtex";

interface LiteratureRecord {
  Title?: string;
  [key: string]: unknown;
}

const route = useRoute();

const table = ref<TableName>("Literature");
const id = ref(route.params.id as string);

const { data: literature, isLoading: loading } =
  useRecordDetails<LiteratureRecord>(table, id);

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  literature,
  literatureConfig,
);

const keyLabelLookup = computed(() => {
  const map = new Map();
  computedKeyLabelPairs.value.forEach((pair) => {
    map.set(pair.key, pair);
  });
  return map;
});

// PDF URL extraction
const pdfUrl = computed(() => {
  if (!literature.value) return null;
  return extractPdfUrl(literature.value["Official Source (PDF)"]);
});

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

function exportBibTeX() {
  const bibtex = bibtexContent.value;
  const rawTitle = (literature.value?.Title || "literature") as string;
  const filename = `${sanitizeFilename(rawTitle)}.bib`;
  downloadFile(bibtex, filename, "application/x-bibtex");
}
</script>
