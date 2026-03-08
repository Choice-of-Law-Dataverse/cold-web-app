<template>
  <div>
    <h1 v-if="literature?.title" class="sr-only">
      {{ literature.title }}
    </h1>
    <BaseDetailLayout
      table="Literature"
      :loading="loading"
      :error="error"
      :data="(literature as unknown as Record<string, unknown>) || {}"
      :field-order="entityConfig.fieldOrder"
      :label-overrides="entityConfig.labelOverrides"
      :tooltips="entityConfig.tooltips"
      :show-suggest-edit="true"
    >
      <!-- Title with PDF and Source Link -->
      <template #title="{ value, label }">
        <section v-if="value" class="section-gap">
          <DetailRow :label="label">
            <TitleWithActions>
              {{ value }}
              <template #actions>
                <PdfLink
                  :pdf-field="undefined"
                  :record-id="id"
                  folder-name="literatures"
                />
                <SourceExternalLink
                  :source-url="sourceUrl"
                  :label="sourceLinkLabel"
                  :open-access="!!literature?.openAccessUrl"
                />
              </template>
            </TitleWithActions>
          </DetailRow>
        </section>
      </template>

      <template #publicationTitle="{ value, label }">
        <section v-if="value" class="section-gap">
          <DetailRow :label="label">
            <span class="result-value-small">{{ value }}</span>
          </DetailRow>
        </section>
      </template>

      <template #publisher="{ value, label, tooltip }">
        <section v-if="value" class="section-gap">
          <DetailRow :label="label" :tooltip="tooltip">
            <span class="result-value-small">{{ value }}</span>
          </DetailRow>
        </section>
      </template>

      <!-- BibTeX Export Section -->
      <template #abstractNote>
        <section class="section-gap">
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

      <template #footer>
        <LastModified :date="literature?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[literature?.title as string]"
      fallback="Literature"
    />

    <EntityFeedback
      entity-type="literature"
      :entity-id="id"
      :entity-title="literature?.title as string"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import { useLiterature } from "@/composables/useRecordDetails";
import DetailRow from "@/components/ui/DetailRow.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import TitleWithActions from "@/components/ui/TitleWithActions.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { generateBibTeX, sanitizeFilename, downloadFile } from "@/utils/bibtex";
import { getEntityConfig } from "@/config/entityRegistry";

const entityConfig = getEntityConfig("/literature")!;

const route = useRoute();

const id = ref(route.params.coldId as string);

const { data: literature, isLoading: loading, error } = useLiterature(id);

const sourceUrl = computed(() => {
  if (!literature.value) return "";
  if (literature.value.openAccessUrl) {
    return literature.value.openAccessUrl as string;
  }
  return (literature.value.url || "") as string;
});

const sourceLinkLabel = computed(() => {
  if (literature.value?.openAccessUrl) {
    return "Open Access Link";
  }
  return "Link";
});

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
  const rawTitle = (literature.value?.title || "literature") as string;
  const filename = `${sanitizeFilename(rawTitle)}.bib`;
  downloadFile(bibtex, filename, "application/x-bibtex");
}
</script>
