<template>
  <div>
    <BaseDetailLayout
      table="Domestic Instruments"
      :loading="loading"
      :error="error"
      :data="legalInstrument || {}"
      :labels="domesticInstrumentLabels"
      :tooltips="domesticInstrumentTooltips"
      :show-suggest-edit="true"
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
                :record-id="instrumentId"
                folder-name="domestic-instruments"
              />
              <SourceExternalLink
                :source-url="legalInstrument?.['Source (URL)']"
              />
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
                legalInstrument?.Abbreviation ||
                legalInstrument?.['Title (in English)'] ||
                ''
              "
              @update:has-english-translation="hasEnglishTranslation = $event"
            />
          </div>
        </DetailRow>
      </template>

      <template #footer>
        <LastModified :date="legalInstrument?.['Last Modified']" />
        <LazyJurisdictionReportBanner
          :jurisdiction-code="legalInstrument?.['Jurisdictions Alpha-3 Code']"
        />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[legalInstrument?.['Title (in English)']]"
      fallback="Domestic Instrument"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, defineAsyncComponent } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import LegalProvision from "@/components/legal/LegalProvision.vue";
import InstrumentLink from "@/components/legal/InstrumentLink.vue";
import CompatibleLabel from "@/components/ui/CompatibleLabel.vue";
import LastModified from "@/components/ui/LastModified.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useDomesticInstrument } from "@/composables/useRecordDetails";
import { getSortedProvisionIds } from "@/utils/provision-sorting";
import { domesticInstrumentLabels } from "@/config/labels";
import { domesticInstrumentTooltips } from "@/config/tooltips";

const LazyJurisdictionReportBanner = defineAsyncComponent(
  () => import("@/components/ui/JurisdictionReportBanner.vue"),
);

const route = useRoute();
const textType = ref("Full Text of the Provision (English Translation)");
const hasEnglishTranslation = ref(false);

// Capture the ID once at setup to prevent flash during page transitions
const instrumentId = ref(route.params.id as string);

const {
  data: legalInstrument,
  isLoading: loading,
  error,
} = useDomesticInstrument(instrumentId);

const isCompatible = (
  field:
    | "Compatible With the UNCITRAL Model Law"
    | "Compatible With the HCCH Principles",
): boolean => {
  if (!legalInstrument.value) return false;
  const value = legalInstrument.value[field];
  return value === true || value === "true";
};

const getSortedProvisionIdsForInstrument = (rawValue: string): string[] => {
  return getSortedProvisionIds(
    rawValue,
    legalInstrument.value?.["Ranking (Display Order)"],
  );
};
</script>
