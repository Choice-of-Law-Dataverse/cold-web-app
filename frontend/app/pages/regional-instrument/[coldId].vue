<template>
  <div>
    <h1 v-if="regionalInstrument?.abbreviation" class="sr-only">
      {{ regionalInstrument.abbreviation }}
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
        <DetailRow :label="regionalInstrumentLabels.abbreviation">
          <TitleWithActions>
            {{ value }}
            <template #actions>
              <PdfLink
                :pdf-field="regionalInstrument?.attachment"
                :record-id="route.params.coldId as string"
                folder-name="regional-instruments"
              />
              <SourceExternalLink :source-url="regionalInstrument?.url" />
            </template>
          </TitleWithActions>
        </DetailRow>
      </template>

      <template #literature>
        <DetailRow
          :label="regionalInstrumentLabels.literature"
          :tooltip="regionalInstrumentTooltips.literature"
        >
          <RelatedItemsList
            :items="relatedLiterature"
            base-path="/literature"
            :empty-value-behavior="{ action: 'hide' }"
          />
        </DetailRow>
      </template>

      <!-- Slot for Legal provisions -->
      <template #regionallegalprovisions>
        <DetailRow
          v-if="sortedRegionalProvisions.length"
          :label="regionalInstrumentLabels.regionalLegalProvisions"
          :tooltip="regionalInstrumentTooltips.regionalLegalProvisions"
        >
          <div class="provisions-container">
            <LegalProvision
              v-for="provision in sortedRegionalProvisions"
              :key="provision.coldId ?? provision.id"
              :provision-id="provision.coldId!"
              :instrument-title="
                regionalInstrument?.abbreviation ||
                regionalInstrument?.title ||
                ''
              "
              table="Regional Legal Provisions"
            />
          </div>
        </DetailRow>
      </template>

      <template #footer>
        <LastModified :date="regionalInstrument?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[regionalInstrument?.abbreviation]"
      fallback="Regional Instrument"
    />

    <EntityFeedback
      entity-type="regional_instrument"
      :entity-id="instrumentId"
      :entity-title="(regionalInstrument?.abbreviation as string) || undefined"
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
import { useRegionalInstrument } from "@/composables/useRecordDetails";
import LegalProvision from "@/components/legal/LegalProvision.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { regionalInstrumentLabels } from "@/config/labels";
import { regionalInstrumentTooltips } from "@/config/tooltips";
import type { RelatedItem } from "@/types/ui";

const route = useRoute();
const instrumentId = ref(route.params.coldId as string);

const {
  data: regionalInstrument,
  isLoading: loading,
  error,
} = useRegionalInstrument(instrumentId);

const relatedLiterature = computed<RelatedItem[]>(() =>
  (regionalInstrument.value?.relations.literature ?? []).map((lit) => ({
    id: lit.coldId || String(lit.id),
    title: lit.title || String(lit.id),
    ...(lit.oupJdChapter
      ? { badge: { label: "OUP", color: "var(--color-label-oup)" } }
      : {}),
  })),
);

const sortedRegionalProvisions = computed(() =>
  (regionalInstrument.value?.relations.regionalLegalProvisions ?? []).filter(
    (p) => p.coldId,
  ),
);
</script>
