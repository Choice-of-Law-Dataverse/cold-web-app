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
          <RelatedItemsList
            :items="relatedLiterature"
            base-path="/literature"
          />
        </DetailRow>
      </template>

      <template #selectedprovisions>
        <DetailRow
          :label="internationalInstrumentLabels.selectedProvisions"
          :tooltip="internationalInstrumentTooltips.selectedProvisions"
        >
          <div class="provisions-container">
            <div v-if="sortedProvisions.length">
              <BaseLegalContent
                v-for="(provision, index) in sortedProvisions"
                :key="index"
                :title="
                  provision.titleOfTheProvision +
                  (internationalInstrument
                    ? ', ' + (internationalInstrument.name || '')
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
            <div v-else-if="!loading">No provisions found.</div>
          </div>
        </DetailRow>
      </template>

      <template #footer>
        <LastModified :date="internationalInstrument?.updatedAt" />
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
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import TitleWithActions from "@/components/ui/TitleWithActions.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import BaseLegalContent from "@/components/legal/BaseLegalContent.vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { useInternationalInstrument } from "@/composables/useRecordDetails";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { internationalInstrumentLabels } from "@/config/labels";
import { internationalInstrumentTooltips } from "@/config/tooltips";
import type { RelatedItem } from "@/types/ui";

const route = useRoute();
const instrumentId = ref(route.params.id as string);

const {
  data: internationalInstrument,
  isLoading: loading,
  error,
} = useInternationalInstrument(instrumentId);

const relatedLiterature = computed<RelatedItem[]>(() =>
  (internationalInstrument.value?.relations.literature ?? [])
    .filter((lit) => !lit.oupJdChapter)
    .map((lit) => ({
      id: lit.coldId || String(lit.id),
      title: lit.title || String(lit.id),
    })),
);

const sortedProvisions = computed(() =>
  [
    ...(internationalInstrument.value?.relations.internationalLegalProvisions ??
      []),
  ].sort(
    (a, b) =>
      (Number(a.rankingDisplayOrder) || 0) -
      (Number(b.rankingDisplayOrder) || 0),
  ),
);

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
