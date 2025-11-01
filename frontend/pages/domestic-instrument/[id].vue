<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="processedLegalInstrument || {}"
      :key-label-pairs="computedKeyLabelPairs"
      :value-class-map="valueClassMap"
      :show-suggest-edit="true"
      source-table="Domestic Instrument"
    >
      <!-- Slot for Amended by -->
      <template #amended-by="{ value }">
        <TwoColumnLayout
          v-if="value"
          :label="keyLabelLookup.get('Amended by')?.label || 'Amended by'"
          :tooltip="keyLabelLookup.get('Amended by')?.tooltip"
        >
          <InstrumentLink :id="value" table="Domestic Instruments" />
        </TwoColumnLayout>
      </template>
      <!-- Slot for Amends -->
      <template #amends="{ value }">
        <TwoColumnLayout
          v-if="value"
          :label="keyLabelLookup.get('Amends')?.label || 'Amends'"
          :tooltip="keyLabelLookup.get('Amends')?.tooltip"
        >
          <InstrumentLink :id="value" table="Domestic Instruments" />
        </TwoColumnLayout>
      </template>
      <!-- Slot for Replaced by -->
      <template #replaced-by="{ value }">
        <TwoColumnLayout
          v-if="value"
          :label="keyLabelLookup.get('Replaced by')?.label || 'Replaced by'"
          :tooltip="keyLabelLookup.get('Replaced by')?.tooltip"
        >
          <InstrumentLink :id="value" table="Domestic Instruments" />
        </TwoColumnLayout>
      </template>
      <!-- Slot for Replaces -->
      <template #replaces="{ value }">
        <TwoColumnLayout
          v-if="value"
          :label="keyLabelLookup.get('Replaces')?.label || 'Replaces'"
          :tooltip="keyLabelLookup.get('Replaces')?.tooltip"
        >
          <InstrumentLink :id="value" table="Domestic Instruments" />
        </TwoColumnLayout>
      </template>
      <!-- Slot for Compatibility section -->
      <template #compatibility="{ value }">
        <TwoColumnLayout
          v-if="
            value &&
            (isCompatible('Compatible With the UNCITRAL Model Law') ||
              isCompatible('Compatible With the HCCH Principles'))
          "
          :label="
            keyLabelLookup.get('Compatibility')?.label || 'Compatible with'
          "
          :tooltip="keyLabelLookup.get('Compatibility')?.tooltip"
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
        </TwoColumnLayout>
      </template>
      <!-- Slot for Legal provisions -->
      <template #domestic-legal-provisions="{ value }">
        <!-- Only render if value exists and is not "N/A" -->
        <TwoColumnLayout
          v-if="value && value.trim() && value.trim() !== 'N/A'"
          :label="
            keyLabelLookup.get('Domestic Legal Provisions')?.label ||
            'Selected Provisions'
          "
          :tooltip="keyLabelLookup.get('Domestic Legal Provisions')?.tooltip"
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
        </TwoColumnLayout>
      </template>
    </BaseDetailLayout>
    <CountryReportLink
      :processed-answer-data="processedLegalInstrument || {}"
    />

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
import TwoColumnLayout from "@/components/ui/TwoColumnLayout.vue";
import LegalProvision from "@/components/legal/LegalProvision.vue";
import InstrumentLink from "@/components/legal/InstrumentLink.vue";
import CompatibleLabel from "@/components/ui/CompatibleLabel.vue";
import CountryReportLink from "@/components/ui/CountryReportLink.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import { legalInstrumentConfig } from "@/config/pageConfigs";
import { getSortedProvisionIds } from "@/utils/provision-sorting";
import type { TableName } from "@/types/api";

interface LegalInstrumentRecord {
  "Title (in English)"?: string;
  "Official Title"?: string;
  Abbreviation?: string;
  "Compatible With the UNCITRAL Model Law"?: boolean | string;
  "Compatible With the HCCH Principles"?: boolean | string;
  "Ranking (Display Order)"?: string;
  [key: string]: unknown;
}

const route = useRoute();
const textType = ref("Full Text of the Provision (English Translation)");
const hasEnglishTranslation = ref(false);

const table = ref<TableName>("Domestic Instruments");
const id = ref(route.params.id as string);

const { data: legalInstrument, isLoading: loading } =
  useRecordDetails<LegalInstrumentRecord>(table, id);

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  legalInstrument,
  legalInstrumentConfig,
);

const keyLabelLookup = computed(() => {
  const map = new Map();
  computedKeyLabelPairs.value.forEach((pair) => {
    map.set(pair.key, pair);
  });
  return map;
});

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

const getSortedProvisionIdsForInstrument = (rawValue: string): string[] => {
  return getSortedProvisionIds(
    rawValue,
    processedLegalInstrument.value?.["Ranking (Display Order)"],
  );
};
</script>
