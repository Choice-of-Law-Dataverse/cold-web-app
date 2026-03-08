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

      <template #specialists>
        <DetailRow
          v-if="specialistItems.length"
          :label="internationalInstrumentLabels.specialists"
          :tooltip="internationalInstrumentTooltips.specialists"
          variant="specialist"
        >
          <RelatedItemsList :items="specialistItems" base-path="/specialist" />
        </DetailRow>
      </template>

      <template #literature>
        <DetailRow
          v-if="relatedLiterature.length"
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
          v-if="provisionItems.length"
          :label="internationalInstrumentLabels.selectedProvisions"
          :tooltip="internationalInstrumentTooltips.selectedProvisions"
        >
          <RelatedItemsList
            :items="provisionItems"
            base-path="/international-legal-provision"
          />
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
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { useInternationalInstrument } from "@/composables/useRecordDetails";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { internationalInstrumentLabels } from "@/config/labels";
import { internationalInstrumentTooltips } from "@/config/tooltips";
import type { RelatedItem } from "@/types/ui";

const route = useRoute();
const instrumentId = ref(route.params.coldId as string);

const {
  data: internationalInstrument,
  isLoading: loading,
  error,
} = useInternationalInstrument(instrumentId);

const relatedLiterature = computed<RelatedItem[]>(() =>
  (internationalInstrument.value?.relations.literature ?? []).map((lit) => ({
    id: lit.coldId || String(lit.id),
    title: lit.title || String(lit.id),
    ...(lit.oupJdChapter
      ? { badge: { label: "OUP", color: "var(--color-label-oup)" } }
      : {}),
  })),
);

const specialistItems = computed<RelatedItem[]>(() =>
  (internationalInstrument.value?.relations.specialists ?? []).map((s) => ({
    id: s.coldId || String(s.id),
    title: s.specialist || String(s.id),
  })),
);

const instrumentTitle = computed(
  () => internationalInstrument.value?.name || "",
);

const provisionItems = computed<RelatedItem[]>(() => {
  const provisions = [
    ...(internationalInstrument.value?.relations.internationalLegalProvisions ??
      []),
  ].sort(
    (a, b) =>
      (Number(a.rankingDisplayOrder) || 0) -
      (Number(b.rankingDisplayOrder) || 0),
  );
  const suffix = instrumentTitle.value ? `, ${instrumentTitle.value}` : "";
  return provisions
    .filter((p) => p.coldId)
    .map((p) => ({
      id: p.coldId || String(p.id),
      title: (p.titleOfTheProvision || p.coldId || String(p.id)) + suffix,
    }));
});
</script>
