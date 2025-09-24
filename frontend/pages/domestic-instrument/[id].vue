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
        <div :class="valueClassMap['Amended by']">
          <SectionRenderer
            v-if="value"
            :id="value"
            section="Amended by"
            :section-label="keyLabelLookup.get('Amended by')?.label"
            :section-tooltip="keyLabelLookup.get('Amended by')?.tooltip"
            table="Domestic Instruments"
            class="mb-8"
          />
        </div>
      </template>
      <!-- Slot for Amends -->
      <template #amends="{ value }">
        <div :class="valueClassMap['Amends']">
          <SectionRenderer
            v-if="value"
            :id="value"
            section="Amends"
            :section-label="keyLabelLookup.get('Amends')?.label"
            :section-tooltip="keyLabelLookup.get('Amends')?.tooltip"
            table="Domestic Instruments"
            class="mb-8"
          />
        </div>
      </template>
      <!-- Slot for Replaced by -->
      <template #replaced-by="{ value }">
        <div :class="valueClassMap['Replaced by']">
          <SectionRenderer
            v-if="value"
            :id="value"
            section="Replaced by"
            :section-label="keyLabelLookup.get('Replaced by')?.label"
            :section-tooltip="keyLabelLookup.get('Replaced by')?.tooltip"
            table="Domestic Instruments"
            class="mb-8"
          />
        </div>
      </template>
      <!-- Slot for Replaces -->
      <template #replaces="{ value }">
        <div :class="valueClassMap['Replaces']">
          <SectionRenderer
            v-if="value"
            :id="value"
            section="Replaces"
            :section-label="keyLabelLookup.get('Replaces')?.label"
            :section-tooltip="keyLabelLookup.get('Replaces')?.tooltip"
            table="Domestic Instruments"
            class="mb-8"
          />
        </div>
      </template>
      <!-- Slot for Compatibility section -->
      <template #compatibility>
        <div v-if="showCompatibility" class="result-value-small section-gap">
          <p class="label mt-12 flex flex-row items-center">
            Compatible with
            <InfoPopover
              v-if="keyLabelLookup.get('Compatibility')?.tooltip"
              :text="keyLabelLookup.get('Compatibility')?.tooltip"
            />
          </p>
          <span v-if="isCompatible('Compatible With the UNCITRAL Model Law?')">
            <CompatibleLabel label="UNCITRAL Model Law" />
          </span>
          <span v-if="isCompatible('Compatible With the HCCH Principles?')">
            <CompatibleLabel label="HCCH Principles" />
          </span>
        </div>
      </template>
      <!-- Slot for Legal provisions -->
      <template #domestic-legal-provisions="{ value }">
        <!-- Only render if value exists and is not "N/A" -->
        <section
          v-if="value && value.trim() && value.trim() !== 'N/A'"
          class="section-gap m-0 p-0"
        >
          <p class="label mb-[-24px] mt-12 flex flex-row items-center">
            {{
              keyLabelLookup.get("Domestic Legal Provisions")?.label ||
              "Selected Provisions"
            }}
            <InfoPopover
              v-if="keyLabelLookup.get('Domestic Legal Provisions')?.tooltip"
              :text="keyLabelLookup.get('Domestic Legal Provisions')?.tooltip"
            />
          </p>
          <div :class="valueClassMap['Domestic Legal Provisions']">
            <div v-if="value && value.trim()">
              <LegalProvision
                v-for="(
                  provisionId, index
                ) in getSortedProvisionIdsForInstrument(value)"
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
          </div>
        </section>
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
import LegalProvision from "@/components/legal/LegalProvision.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import SectionRenderer from "@/components/legal/SectionRenderer.vue";
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
  "Compatible With the UNCITRAL Model Law?"?: boolean | string;
  "Compatible With the HCCH Principles?"?: boolean | string;
  "Ranking (Display Order)"?: string;
  [key: string]: unknown;
}

const route = useRoute();
const textType = ref("Full Text of the Provision (English Translation)");
const hasEnglishTranslation = ref(false);

// Use TanStack Vue Query for data fetching - no need for refs with static values
const table = ref<TableName>("Domestic Instruments");
const id = ref(route.params.id as string);

const { data: legalInstrument, isLoading: loading } =
  useRecordDetails<LegalInstrumentRecord>(table, id);

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  legalInstrument,
  legalInstrumentConfig,
);

// Create lookup map for better performance
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
  return {
    ...legalInstrument.value,
    "Title (in English)":
      legalInstrument.value["Title (in English)"] ||
      legalInstrument.value["Official Title"],
  };
});

// Helper function to check compatibility
const isCompatible = (field: string): boolean => {
  if (!processedLegalInstrument.value) return false;
  const value = (processedLegalInstrument.value as Record<string, unknown>)[
    field
  ];
  return value === true || value === "true";
};

// Computed for compatibility display
const showCompatibility = computed(() => {
  return (
    isCompatible("Compatible With the UNCITRAL Model Law?") ||
    isCompatible("Compatible With the HCCH Principles?")
  );
});

// Simplified sorting function wrapper
const getSortedProvisionIdsForInstrument = (rawValue: string): string[] => {
  return getSortedProvisionIds(
    rawValue,
    processedLegalInstrument.value?.["Ranking (Display Order)"],
  );
};
</script>
