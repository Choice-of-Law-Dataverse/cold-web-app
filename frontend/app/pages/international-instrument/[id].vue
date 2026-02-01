<template>
  <div>
    <BaseDetailLayout
      table="International Instruments"
      :loading="loading"
      :error="error"
      :data="internationalInstrument || {}"
      :labels="internationalInstrumentLabels"
      :tooltips="internationalInstrumentTooltips"
      :show-suggest-edit="true"
    >
      <!-- Name (Title) with PDF and Source Link -->
      <template #name="{ value }">
        <DetailRow :label="internationalInstrumentLabels['Name']">
          <div class="flex items-start justify-between gap-4">
            <div class="result-value-small flex-1">
              {{ value }}
            </div>
            <div class="flex flex-shrink-0 items-center gap-3">
              <PdfLink
                :pdf-field="internationalInstrument?.Attachment"
                :record-id="instrumentId"
                folder-name="international-instruments"
              />
              <SourceExternalLink :source-url="internationalInstrument?.URL" />
            </div>
          </div>
        </DetailRow>
      </template>

      <template #literature>
        <DetailRow
          :label="internationalInstrumentLabels['Literature']"
          :tooltip="internationalInstrumentTooltips['Literature']"
        >
          <LazyRelatedLiterature
            :literature-id="internationalInstrument?.Literature || ''"
            mode="id"
            :oup-filter="'noOup'"
          />
        </DetailRow>
      </template>

      <template #selected-provisions>
        <DetailRow
          :label="internationalInstrumentLabels['Selected Provisions']"
          :tooltip="internationalInstrumentTooltips['Selected Provisions']"
        >
          <div class="provisions-container">
            <div v-if="provisionsLoading">
              <LoadingBar class="!mt-8" />
            </div>
            <div v-else-if="provisionsError">{{ provisionsError }}</div>
            <div v-else-if="provisions && provisions.length">
              <BaseLegalContent
                v-for="(provision, index) in provisions"
                :key="index"
                :title="
                  provision['Title of the Provision'] +
                  (internationalInstrument
                    ? ', ' +
                      (internationalInstrument.Abbreviation ||
                        internationalInstrument['Title (in English)'])
                    : '')
                "
                :anchor-id="
                  normalizeAnchorId(
                    String(provision['Title of the Provision'] || ''),
                  )
                "
              >
                <template #default>
                  {{ provision["Full Text"] }}
                </template>
              </BaseLegalContent>
            </div>
            <div v-else>No provisions found.</div>
          </div>
        </DetailRow>
      </template>

      <template #footer>
        <LastModified :date="internationalInstrument?.['Last Modified']" />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[internationalInstrument?.Name]"
      fallback="International Instrument"
    />
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import BaseLegalContent from "@/components/legal/BaseLegalContent.vue";
import { useInternationalInstrument } from "@/composables/useRecordDetails";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import { useInternationalLegalProvisions } from "@/composables/useFullTable";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { internationalInstrumentLabels } from "@/config/labels";
import { internationalInstrumentTooltips } from "@/config/tooltips";

const LazyRelatedLiterature = defineAsyncComponent(
  () => import("@/components/literature/RelatedLiterature.vue"),
);

const route = useRoute();

// Capture the ID once at setup to prevent flash during page transitions
const instrumentId = ref(route.params.id as string);

const {
  data: internationalInstrument,
  isLoading: loading,
  error,
} = useInternationalInstrument(instrumentId);

const {
  data: provisions,
  isLoading: provisionsLoading,
  error: provisionsError,
} = useInternationalLegalProvisions();

function normalizeAnchorId(str: string): string {
  if (!str) return "";
  return str
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/\s+/g, "-")
    .replace(/[^a-zA-Z0-9\-_]/g, "")
    .toLowerCase();
}
</script>
