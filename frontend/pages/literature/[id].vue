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
                <PdfLink :record-id="id" folder-name="literatures" />
                <a
                  v-if="sourceUrl"
                  :href="sourceUrl"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center gap-1 text-sm"
                  style="color: var(--color-cold-purple)"
                  @click.stop
                >
                  <UIcon
                    name="i-material-symbols:open-in-new"
                    class="h-4 w-4"
                  />
                  <span>{{ sourceLinkLabel }}</span>
                </a>
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
          <DetailRow label="Export as BibTeX">
            <button
              class="link-button flex items-center gap-1"
              @click="exportBibTeX"
            >
              <UIcon
                name="i-material-symbols:download-outline"
                class="h-4 w-4"
              />
              <span>Download BibTeX</span>
            </button>
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
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { literatureConfig } from "@/config/pageConfigs";
import type { TableName } from "@/types/api";

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

// BibTeX export functions
function generateBibTeX() {
  const data = literature.value || {};
  const authors = (data.Authors || data.Author || "") as string;
  const title = (data.Title || "") as string;
  const year = (data.Year || data["Publication Year"] || "") as string;
  const journal = (data["Publication Title"] || data.Journal || "") as string;
  const volume = (data.Volume || "") as string;
  const pages = (data.Pages || "") as string;
  const publisher = (data.Publisher || "") as string;
  const doi = (data.DOI || "") as string;
  const url = (data.Url || data.URL || "") as string;

  // Generate citation key from first author's last name and year
  let citationKey = "cold_literature";
  if (authors && year) {
    const firstAuthor = authors.split(",")[0].trim().split(" ").pop();
    // Clean the author name for use in citation key
    const cleanAuthor = firstAuthor
      ?.replace(/[^a-zA-Z]/g, "")
      .toLowerCase();
    citationKey = `${cleanAuthor}${year}`;
  } else if (title && year) {
    // Fallback to first word of title + year
    const firstWord = title
      .split(" ")[0]
      .replace(/[^a-zA-Z]/g, "")
      .toLowerCase();
    citationKey = `${firstWord}${year}`;
  }

  // Escape special BibTeX characters in strings
  const escape = (str: string) =>
    str.replace(/[{}\\]/g, (char) => `\\${char}`).replace(/%/g, "\\%");

  let bibtex = `@article{${citationKey},\n`;
  if (authors) bibtex += `  author = {${escape(authors)}},\n`;
  if (title) bibtex += `  title = {${escape(title)}},\n`;
  if (journal) bibtex += `  journal = {${escape(journal)}},\n`;
  if (year) bibtex += `  year = {${year}},\n`;
  if (volume) bibtex += `  volume = {${volume}},\n`;
  if (pages) bibtex += `  pages = {${pages}},\n`;
  if (publisher) bibtex += `  publisher = {${escape(publisher)}},\n`;
  if (doi) bibtex += `  doi = {${doi}},\n`;
  if (url) bibtex += `  url = {${url}},\n`;
  bibtex += "}";

  return bibtex;
}

function sanitizeFilename(filename: string) {
  return filename
    .replace(/[<>:"/\\|?*]/g, "") // Remove invalid characters
    .replace(/\s+/g, "_") // Replace spaces with underscores
    .substring(0, 200); // Limit length
}

function downloadFile(content: string, filename: string, mimeType: string) {
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

function exportBibTeX() {
  const bibtex = generateBibTeX();
  const rawTitle = (literature.value?.Title || "literature") as string;
  const filename = `${sanitizeFilename(rawTitle)}.bib`;
  downloadFile(bibtex, filename, "application/x-bibtex");
}
</script>
