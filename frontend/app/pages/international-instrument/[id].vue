<template>
  <div>
    <h1 v-if="internationalInstrument?.name" class="sr-only">
      {{ internationalInstrument.name }}
    </h1>
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
        <DetailRow :label="internationalInstrumentLabels.name">
          <TitleWithActions>
            {{ value }}
            <template #actions>
              <PdfLink
                :pdf-field="internationalInstrument?.attachment"
                :record-id="instrumentId"
                folder-name="international-instruments"
              />
              <SourceExternalLink
                :source-url="internationalInstrument?.displayUrl"
              />
            </template>
          </TitleWithActions>
        </DetailRow>
      </template>

      <template #literature>
        <DetailRow
          :label="internationalInstrumentLabels.literature"
          :tooltip="internationalInstrumentTooltips.literature"
        >
          <LazyRelatedLiterature
            :literature-id="internationalInstrument?.literature || ''"
            mode="id"
            :oup-filter="'noOup'"
          />
        </DetailRow>
      </template>

      <template #selectedprovisions>
        <DetailRow
          :label="internationalInstrumentLabels.selectedProvisions"
          :tooltip="internationalInstrumentTooltips.selectedProvisions"
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
                  provision.titleOfTheProvision +
                  (internationalInstrument
                    ? ', ' +
                      (internationalInstrument.abbreviation ||
                        internationalInstrument.titleInEnglish)
                    : '')
                "
                :anchor-id="
                  normalizeAnchorId(String(provision.titleOfTheProvision || ''))
                "
              >
                <template #default>
                  {{ provision.fullText }}
                </template>
              </BaseLegalContent>
            </div>
            <div v-else>No provisions found.</div>
          </div>
        </DetailRow>
      </template>

      <template #footer>
        <LastModified
          :date="internationalInstrument?.lastModified ?? undefined"
        />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[internationalInstrument?.name]"
      fallback="International Instrument"
    />

    <EntityFeedback
      entity-type="international_instrument"
      :entity-id="instrumentId"
      :entity-title="(internationalInstrument?.name as string) || undefined"
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
import BaseLegalContent from "@/components/legal/BaseLegalContent.vue";
import { useInternationalInstrument } from "@/composables/useRecordDetails";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import { useInternationalLegalProvisions } from "@/composables/useFullTable";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
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
