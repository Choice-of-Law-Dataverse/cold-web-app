<template>
  <div>
    <h1 v-if="legalInstrument?.titleInEnglish" class="sr-only">
      {{ legalInstrument.titleInEnglish }}
    </h1>
    <BaseDetailLayout
      table="Domestic Instruments"
      :loading="loading"
      :error="error"
      :data="legalInstrument || {}"
      :labels="domesticInstrumentLabels"
      :tooltips="domesticInstrumentTooltips"
      :relations="legalInstrument?.relations"
      :show-suggest-edit="true"
    >
      <template #titleinenglish="{ value }">
        <DetailRow
          :label="domesticInstrumentLabels.titleInEnglish"
          :tooltip="domesticInstrumentTooltips.titleInEnglish"
        >
          <TitleWithActions>
            {{ value }}
            <template #actions>
              <PdfLink
                :pdf-field="legalInstrument?.sourcePdf"
                :record-id="instrumentId"
                folder-name="domestic-instruments"
              />
              <SourceExternalLink :source-url="legalInstrument?.sourceUrl" />
            </template>
          </TitleWithActions>
        </DetailRow>
      </template>

      <template #amendedby="{ value }">
        <DetailRow v-if="value" :label="domesticInstrumentLabels.amendedBy">
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <template #amends="{ value }">
        <DetailRow v-if="value" :label="domesticInstrumentLabels.amends">
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <template #replacedby="{ value }">
        <DetailRow v-if="value" :label="domesticInstrumentLabels.replacedBy">
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <template #replaces="{ value }">
        <DetailRow v-if="value" :label="domesticInstrumentLabels.replaces">
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <template #compatibility="{ value }">
        <DetailRow
          v-if="
            value &&
            (isCompatible('compatibleWithTheUncitralModelLaw') ||
              isCompatible('compatibleWithTheHcchPrinciples'))
          "
          :label="domesticInstrumentLabels.compatibility"
          :tooltip="domesticInstrumentTooltips.compatibility"
        >
          <div class="result-value-small flex gap-2">
            <CompatibleLabel
              v-if="isCompatible('compatibleWithTheUncitralModelLaw')"
              label="UNCITRAL Model Law"
            />
            <CompatibleLabel
              v-if="isCompatible('compatibleWithTheHcchPrinciples')"
              label="HCCH Principles"
            />
          </div>
        </DetailRow>
      </template>

      <template #footer>
        <JurisdictionReportBanner
          :jurisdiction-code="primaryJurisdiction?.coldId ?? undefined"
          :jurisdiction-name="primaryJurisdiction?.name ?? undefined"
        />
        <LastModified :date="legalInstrument?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[legalInstrument?.titleInEnglish]"
      fallback="Domestic Instrument"
    />

    <EntityFeedback
      entity-type="domestic_instrument"
      :entity-id="instrumentId"
      :entity-title="legalInstrument?.titleInEnglish as string"
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
import InstrumentLink from "@/components/legal/InstrumentLink.vue";
import CompatibleLabel from "@/components/ui/CompatibleLabel.vue";
import JurisdictionReportBanner from "@/components/jurisdiction/JurisdictionReportBanner.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { useDomesticInstrument } from "@/composables/useRecordDetails";
import { isTruthy } from "@/types/entities/domestic-instrument";
import { domesticInstrumentLabels } from "@/config/labels";
import { domesticInstrumentTooltips } from "@/config/tooltips";

const route = useRoute();

const instrumentId = ref(route.params.coldId as string);

const {
  data: legalInstrument,
  isLoading: loading,
  error,
} = useDomesticInstrument(instrumentId);

const primaryJurisdiction = computed(
  () => legalInstrument.value?.relations.jurisdictions[0] ?? null,
);

const isCompatible = (
  field:
    | "compatibleWithTheUncitralModelLaw"
    | "compatibleWithTheHcchPrinciples",
): boolean => {
  if (!legalInstrument.value) return false;
  return isTruthy(legalInstrument.value[field]);
};
</script>
