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
      :field-order="entityConfig.fieldOrder"
      :label-overrides="entityConfig.labelOverrides"
      :tooltips="entityConfig.tooltips"
      :relations="legalInstrument?.relations"
      :show-suggest-edit="true"
    >
      <template #titleInEnglish="{ value, label, tooltip }">
        <DetailRow :label="label" :tooltip="tooltip">
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

      <template #amendedBy="{ value, label }">
        <DetailRow v-if="value" :label="label">
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <template #amends="{ value, label }">
        <DetailRow v-if="value" :label="label">
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <template #replacedBy="{ value, label }">
        <DetailRow v-if="value" :label="label">
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <template #replaces="{ value, label }">
        <DetailRow v-if="value" :label="label">
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <template #compatibility="{ value, label, tooltip }">
        <DetailRow
          v-if="
            value &&
            (isCompatible('compatibleWithTheUncitralModelLaw') ||
              isCompatible('compatibleWithTheHcchPrinciples'))
          "
          :label="label"
          :tooltip="tooltip"
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
import { getEntityConfig } from "@/config/entityRegistry";

const entityConfig = getEntityConfig("/domestic-instrument")!;

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
