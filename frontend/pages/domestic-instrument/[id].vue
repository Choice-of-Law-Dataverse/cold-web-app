<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="processedLegalInstrument || {}"
      :labels="domesticInstrumentLabels"
      :tooltips="domesticInstrumentTooltips"
      :show-suggest-edit="true"
      source-table="Domestic Instrument"
    >
      <!-- Title with PDF and Source Link -->
      <template #title-(in-english)="{ value }">
        <DetailRow
          :label="domesticInstrumentLabels['Title (in English)']"
          :tooltip="domesticInstrumentTooltips['Title (in English)']"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="result-value-small flex-1">
              {{ value }}
            </div>
            <div class="flex flex-shrink-0 items-center gap-3">
              <PdfLink
                :pdf-field="
                  legalInstrument?.['Official Source (PDF)'] ||
                  legalInstrument?.['Source (PDF)']
                "
                :record-id="route.params.id as string"
                folder-name="domestic-instruments"
              />
              <SourceExternalLink :source-url="sourceUrl" />
            </div>
          </div>
        </DetailRow>
      </template>

      <!-- Slot for Amended by -->
      <template #amended-by="{ value }">
        <DetailRow v-if="value" :label="domesticInstrumentLabels['Amended by']">
          <InstrumentLink :id="value" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <!-- Slot for Amends -->
      <template #amends="{ value }">
        <DetailRow v-if="value" :label="domesticInstrumentLabels['Amends']">
          <InstrumentLink :id="value" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <!-- Slot for Replaced by -->
      <template #replaced-by="{ value }">
        <DetailRow
          v-if="value"
          :label="domesticInstrumentLabels['Replaced by']"
        >
          <InstrumentLink :id="value" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <!-- Slot for Replaces -->
      <template #replaces="{ value }">
        <DetailRow v-if="value" :label="domesticInstrumentLabels['Replaces']">
          <InstrumentLink :id="value" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <!-- Slot for Compatibility section -->
      <template #compatibility="{ value }">
        <DetailRow
          v-if="
            value &&
            (isCompatible('Compatible With the UNCITRAL Model Law') ||
              isCompatible('Compatible With the HCCH Principles'))
          "
          :label="domesticInstrumentLabels['Compatibility']"
          :tooltip="domesticInstrumentTooltips['Compatibility']"
        >
          <div class="result-value-small flex gap-2">
            <CompatibleLabel
              v-if="isCompatible('Compatible With the UNCITRAL Model Law')"
              label="UNCITRAL Model Law"
            />
            <CompatibleLabel
              v-if="isCompatible('Compatible With the HCCH Principles')"
              label="HCCH Principles"
            />
          </div>
        </DetailRow>
      </template>
      <!-- Slot for Legal provisions -->
      <template #domestic-legal-provisions="{ value }">
        <!-- Only render if value exists and is not "N/A" -->
        <DetailRow
          v-if="value && value.trim() && value.trim() !== 'N/A'"
          :label="domesticInstrumentLabels['Domestic Legal Provisions']"
          :tooltip="domesticInstrumentTooltips['Domestic Legal Provisions']"
        >
          <div class="provisions-container">
            <LegalProvision
              v-for="(provisionId, index) in getSortedProvisionIdsForInstrument(
                value,
              )"
              :key="index"
              :provision-id="provisionId"
              :text-type="textType"
              :instrument-title="
                processedLegalInstrument
                  ? processedLegalInstrument['Abbreviation'] ||
                    processedLegalInstrument['Title (in English)']
                  : ''
              "
              @update:has-english-translation="hasEnglishTranslation = $event"
            />
          </div>
        </DetailRow>
      </template>

      <template #country-report>
        <CountryReportLink
          :jurisdiction-code="
            processedLegalInstrument?.['Jurisdictions Alpha-3 Code'] as string
          "
        />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[
        processedLegalInstrument?.['Title (in English)'] as string,
      ]"
      fallback="Domestic Instrument"
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
import LegalProvision from "@/components/legal/LegalProvision.vue";
import InstrumentLink from "@/components/legal/InstrumentLink.vue";
import CompatibleLabel from "@/components/ui/CompatibleLabel.vue";
import CountryReportLink from "@/components/ui/CountryReportLink.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { getSortedProvisionIds } from "@/utils/provision-sorting";
import type { TableName } from "@/types/api";
import { domesticInstrumentLabels } from "@/config/labels";
import { domesticInstrumentTooltips } from "@/config/tooltips";

interface LegalInstrumentRecord {
  "Title (in English)"?: string;
  "Official Title"?: string;
  Abbreviation?: string;
  "Compatible With the UNCITRAL Model Law"?: boolean | string;
  "Compatible With the HCCH Principles"?: boolean | string;
  "Ranking (Display Order)"?: string;
  "Jurisdictions Alpha-3 Code"?: string;
  [key: string]: unknown;
}

const route = useRoute();
const textType = ref("Full Text of the Provision (English Translation)");
const hasEnglishTranslation = ref(false);

const table = ref<TableName>("Domestic Instruments");
const id = ref(route.params.id as string);

const { data: legalInstrument, isLoading: loading } =
  useRecordDetails<LegalInstrumentRecord>(table, id);

const processedLegalInstrument = computed(() => {
  if (!legalInstrument.value) {
    return null;
  }

  const hasCompatibility =
    legalInstrument.value["Compatible With the UNCITRAL Model Law"] === true ||
    legalInstrument.value["Compatible With the HCCH Principles"] === true;

  return {
    ...legalInstrument.value,
    "Title (in English)":
      legalInstrument.value["Title (in English)"] ||
      legalInstrument.value["Official Title"],
    Compatibility: hasCompatibility ? true : undefined,
  };
});

const isCompatible = (field: string): boolean => {
  if (!processedLegalInstrument.value) return false;
  const value = (processedLegalInstrument.value as Record<string, unknown>)[
    field
  ];
  return value === true || value === "true";
};

// Source URL for domestic instruments
const sourceUrl = computed(() => {
  return (legalInstrument.value?.["Source (URL)"] || "") as string;
});

const getSortedProvisionIdsForInstrument = (rawValue: string): string[] => {
  return getSortedProvisionIds(
    rawValue,
    processedLegalInstrument.value?.["Ranking (Display Order)"],
  );
};
</script>
