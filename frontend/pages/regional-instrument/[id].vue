<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="processedRegionalInstrument || {}"
      :labels="regionalInstrumentLabels"
      :tooltips="regionalInstrumentTooltips"
      :show-suggest-edit="true"
      source-table="Regional Instrument"
    >
      <!-- Abbreviation with PDF and Source Link -->
      <template #abbreviation="{ value }">
        <DetailRow :label="regionalInstrumentLabels['Abbreviation']">
          <div class="flex items-start justify-between gap-4">
            <div class="result-value-small flex-1">
              {{ value }}
            </div>
            <div class="flex flex-shrink-0 items-center gap-3">
              <PdfLink
                :pdf-field="regionalInstrument?.['Attachment']"
                :record-id="route.params.id as string"
                folder-name="regional-instruments"
              />
              <SourceExternalLink
                :source-url="processedRegionalInstrument?.URL"
              />
            </div>
          </div>
        </DetailRow>
      </template>

      <template #literature>
        <DetailRow
          :label="regionalInstrumentLabels['Literature']"
          :tooltip="regionalInstrumentTooltips['Literature']"
        >
          <RelatedLiterature
            :literature-id="
              (processedRegionalInstrument?.Literature as string) || ''
            "
            mode="id"
            :oup-filter="'noOup'"
          />
        </DetailRow>
      </template>

      <!-- Slot for Legal provisions -->
      <template #regional-legal-provisions="{ value }">
        <!-- Only render if value exists and is not "N/A" -->
        <DetailRow
          v-if="value && value.trim() && value.trim() !== 'N/A'"
          :label="regionalInstrumentLabels['Regional Legal Provisions']"
          :tooltip="regionalInstrumentTooltips['Regional Legal Provisions']"
        >
          <div class="provisions-container">
            <LegalProvision
              v-for="(provisionId, index) in value.split(',')"
              :key="index"
              :provision-id="provisionId"
              :text-type="textType"
              :instrument-title="
                processedRegionalInstrument
                  ? (processedRegionalInstrument['Abbreviation'] as string) ||
                    (processedRegionalInstrument['Title'] as string)
                  : ''
              "
              table="Regional Legal Provisions"
              @update:has-english-translation="hasEnglishTranslation = $event"
            />
          </div>
        </DetailRow>
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[
        processedRegionalInstrument?.['Abbreviation'] as string,
      ]"
      fallback="Regional Instrument"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import RelatedLiterature from "@/components/literature/RelatedLiterature.vue";
import LegalProvision from "@/components/legal/LegalProvision.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import type { TableName } from "@/types/api";
import { regionalInstrumentLabels } from "@/config/labels";
import { regionalInstrumentTooltips } from "@/config/tooltips";

interface RegionalInstrumentRecord {
  Abbreviation?: string;
  "Official Title"?: string;
  [key: string]: unknown;
}

const route = useRoute();
const textType = ref("Full Text of the Provision (English Translation)");
const hasEnglishTranslation = ref(false);

const table = ref<TableName>("Regional Instruments");
const id = ref(route.params.id as string);

const { data: regionalInstrument, isLoading: loading } =
  useRecordDetails<RegionalInstrumentRecord>(table, id);

const processedRegionalInstrument = computed(() => {
  if (!regionalInstrument.value) return null;
  return {
    ...regionalInstrument.value,
    "Title (in English)":
      regionalInstrument.value["Title (in English)"] ||
      regionalInstrument.value["Name"],
    Date: regionalInstrument.value["Date"],
    URL: regionalInstrument.value["URL"] || regionalInstrument.value["Link"],
    Title: (regionalInstrument.value as Record<string, unknown>)["Title"],
    Literature: (regionalInstrument.value as Record<string, unknown>)[
      "Literature"
    ],
  };
});
</script>
