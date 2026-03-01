<template>
  <div>
    <h1 v-if="regionalInstrument?.Abbreviation" class="sr-only">
      {{ regionalInstrument.Abbreviation }}
    </h1>
    <BaseDetailLayout
      table="Regional Instruments"
      :loading="loading"
      :error="error"
      :data="regionalInstrument || {}"
      :labels="regionalInstrumentLabels"
      :tooltips="regionalInstrumentTooltips"
      :show-suggest-edit="true"
    >
      <!-- Abbreviation with PDF and Source Link -->
      <template #abbreviation="{ value }">
        <DetailRow :label="regionalInstrumentLabels['Abbreviation']">
          <TitleWithActions>
            {{ value }}
            <template #actions>
              <PdfLink
                :pdf-field="regionalInstrument?.Attachment"
                :record-id="route.params.id as string"
                folder-name="regional-instruments"
              />
              <SourceExternalLink :source-url="regionalInstrument?.URL" />
            </template>
          </TitleWithActions>
        </DetailRow>
      </template>

      <template #literature>
        <DetailRow
          :label="regionalInstrumentLabels['Literature']"
          :tooltip="regionalInstrumentTooltips['Literature']"
        >
          <LazyRelatedLiterature
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

      <template #footer>
        <LastModified :date="regionalInstrument?.['Last Modified']" />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[regionalInstrument?.Abbreviation]"
      fallback="Regional Instrument"
    />

    <EntityFeedback
      entity-type="regional_instrument"
      :entity-id="instrumentId"
      :entity-title="regionalInstrument?.Abbreviation as string"
    />
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import TitleWithActions from "@/components/ui/TitleWithActions.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import { useRegionalInstrument } from "@/composables/useRecordDetails";
import LegalProvision from "@/components/legal/LegalProvision.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { regionalInstrumentLabels } from "@/config/labels";
import { regionalInstrumentTooltips } from "@/config/tooltips";

const LazyRelatedLiterature = defineAsyncComponent(
  () => import("@/components/literature/RelatedLiterature.vue"),
);

const route = useRoute();

// Capture the ID once at setup to prevent flash during page transitions
const instrumentId = ref(route.params.id as string);

const {
  data: regionalInstrument,
  isLoading: loading,
  error,
} = useRegionalInstrument(instrumentId);
</script>
