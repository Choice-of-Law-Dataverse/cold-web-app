<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="regionalInstrument || {}"
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
                :pdf-field="regionalInstrument?.Attachment"
                :record-id="route.params.id as string"
                folder-name="regional-instruments"
              />
              <SourceExternalLink :source-url="regionalInstrument?.URL" />
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
            :literature-id="regionalInstrument?.Literature || ''"
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
              :instrument-title="
                regionalInstrument?.Abbreviation ||
                regionalInstrument?.Title ||
                ''
              "
              table="Regional Legal Provisions"
            />
          </div>
        </DetailRow>
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[regionalInstrument?.Abbreviation]"
      fallback="Regional Instrument"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import { useRegionalInstrument } from "@/composables/useRegionalInstrument";
import RelatedLiterature from "@/components/literature/RelatedLiterature.vue";
import LegalProvision from "@/components/legal/LegalProvision.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { regionalInstrumentLabels } from "@/config/labels";
import { regionalInstrumentTooltips } from "@/config/tooltips";

const route = useRoute();

const { data: regionalInstrument, isLoading: loading } = useRegionalInstrument(
  computed(() => route.params.id as string),
);
</script>
