<template>
  <UModal
    :model-value="modelValue"
    :ui="{ rounded: 'rounded-none' }"
    @update:model-value="(v) => emit('update:modelValue', v)"
  >
    <div class="p-6">
      <h2 class="mb-4">Export</h2>
      <p class="result-value-small mb-4">
        Choose an export format for this {{ pageType }}:
      </p>

      <div class="flex flex-col gap-3">
        <!-- BibTeX Export (for Literature) -->
        <button
          v-if="pageType === 'Literature'"
          class="link-button flex items-center justify-between"
          @click="exportBibTeX"
        >
          <span>Export as BibTeX</span>
          <UIcon
            name="i-material-symbols:download-outline"
            class="relative top-[1px] inline-block"
          />
        </button>

        <!-- JSON Export (for all types) -->
        <button
          class="link-button flex items-center justify-between"
          @click="exportJSON"
        >
          <span>Export as JSON</span>
          <UIcon
            name="i-material-symbols:download-outline"
            class="relative top-[1px] inline-block"
          />
        </button>

        <!-- Print -->
        <button
          class="link-button flex items-center justify-between"
          @click="printPage"
        >
          <span>Print Page</span>
          <UIcon
            name="i-material-symbols:print-outline"
            class="relative top-[1px] inline-block"
          />
        </button>
      </div>
    </div>
  </UModal>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  resultData: { type: Object, default: () => ({}) },
  pageType: { type: String, default: "" },
});

const emit = defineEmits(["update:modelValue"]);

const route = useRoute();

function slugToPageType(slug) {
  switch (slug) {
    case "jurisdiction":
      return "Country Report";
    case "court-decision":
      return "Court Decision";
    case "domestic-instrument":
      return "Domestic Instrument";
    case "regional-instrument":
      return "Regional Instrument";
    case "international-instrument":
      return "International Instrument";
    case "arbitral-rule":
      return "Arbitral Rule";
    case "arbitral-award":
      return "Arbitral Award";
    case "literature":
      return "Literature";
    case "question":
      return "Question";
    default:
      return slug
        .split("-")
        .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
        .join(" ");
  }
}

const pageType = computed(() => {
  if (props.pageType) return props.pageType;
  const segments = route.path.split("/").filter(Boolean);
  return slugToPageType(segments[0] || "");
});

function generateBibTeX() {
  const data = props.resultData;
  const authors = data.Authors || data.Author || "";
  const title = data.Title || "";
  const year = data.Year || data["Publication Year"] || "";
  const journal = data["Publication Title"] || data.Journal || "";
  const volume = data.Volume || "";
  const pages = data.Pages || "";
  const publisher = data.Publisher || "";
  const doi = data.DOI || "";
  const url = data.Url || data.URL || "";

  // Generate citation key from first author's last name and year
  let citationKey = "unknown";
  if (authors && year) {
    const firstAuthor = authors.split(",")[0].trim().split(" ").pop();
    citationKey = `${firstAuthor}${year}`;
  }

  let bibtex = `@article{${citationKey},\n`;
  if (authors) bibtex += `  author = {${authors}},\n`;
  if (title) bibtex += `  title = {${title}},\n`;
  if (journal) bibtex += `  journal = {${journal}},\n`;
  if (year) bibtex += `  year = {${year}},\n`;
  if (volume) bibtex += `  volume = {${volume}},\n`;
  if (pages) bibtex += `  pages = {${pages}},\n`;
  if (publisher) bibtex += `  publisher = {${publisher}},\n`;
  if (doi) bibtex += `  doi = {${doi}},\n`;
  if (url) bibtex += `  url = {${url}},\n`;
  bibtex += "}";

  return bibtex;
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

function exportBibTeX() {
  const bibtex = generateBibTeX();
  const filename = `${props.resultData.Title || "literature"}.bib`;
  downloadFile(bibtex, filename, "application/x-bibtex");
  emit("update:modelValue", false);
}

function exportJSON() {
  const json = JSON.stringify(props.resultData, null, 2);
  const title =
    props.resultData.Title ||
    props.resultData["Case Title"] ||
    props.resultData.Name ||
    props.resultData["Case Citation"] ||
    "export";
  const filename = `${title.replace(/[^a-z0-9]/gi, "_").toLowerCase()}.json`;
  downloadFile(json, filename, "application/json");
  emit("update:modelValue", false);
}

function printPage() {
  emit("update:modelValue", false);
  setTimeout(() => {
    window.print();
  }, 100);
}
</script>
