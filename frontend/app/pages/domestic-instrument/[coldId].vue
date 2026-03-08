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
      :show-suggest-edit="true"
    >
      <!-- Title with PDF and Source Link -->
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

      <!-- Slot for Amended by -->
      <template #amendedby="{ value }">
        <DetailRow v-if="value" :label="domesticInstrumentLabels.amendedBy">
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <!-- Slot for Amends -->
      <template #amends="{ value }">
        <DetailRow v-if="value" :label="domesticInstrumentLabels.amends">
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <!-- Slot for Replaced by -->
      <template #replacedby="{ value }">
        <DetailRow v-if="value" :label="domesticInstrumentLabels.replacedBy">
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <!-- Slot for Replaces -->
      <template #replaces="{ value }">
        <DetailRow v-if="value" :label="domesticInstrumentLabels.replaces">
          <InstrumentLink :id="value as string" table="Domestic Instruments" />
        </DetailRow>
      </template>
      <!-- Slot for Compatibility section -->
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
      <!-- Slot for Legal provisions -->
      <template #domesticlegalprovisions>
        <DetailRow
          v-if="sortedProvisions.length"
          :label="domesticInstrumentLabels.domesticLegalProvisions"
          :tooltip="domesticInstrumentTooltips.domesticLegalProvisions"
        >
          <div class="provisions-container">
            <LegalProvision
              v-for="provision in sortedProvisions"
              :key="provision.coldId ?? provision.id"
              :provision-id="provision.coldId!"
              :text-type="textType"
              :instrument-title="
                legalInstrument?.abbreviation ||
                legalInstrument?.titleInEnglish ||
                ''
              "
              @update:has-english-translation="hasEnglishTranslation = $event"
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
import LegalProvision from "@/components/legal/LegalProvision.vue";
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
const textType = ref("fullTextOfTheProvisionEnglishTranslation");
const hasEnglishTranslation = ref(false);

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

const sortedProvisions = computed(() => {
  const provisions =
    legalInstrument.value?.relations.domesticLegalProvisions ?? [];
  const filtered = provisions.filter((p) => p.coldId);
  const rankingStr = legalInstrument.value?.rankingDisplayOrder;
  if (!rankingStr) return filtered;

  const rankingMap: Record<string, number> = {};
  rankingStr.split(",").forEach((pair) => {
    const [coldId, rank] = pair.split(/:(?=[^:]*$)/);
    if (coldId && rank && !isNaN(Number(rank))) {
      rankingMap[coldId.trim()] = Number(rank.trim());
    }
  });

  return [...filtered].sort((a, b) => {
    const ra = rankingMap[a.coldId!];
    const rb = rankingMap[b.coldId!];
    if (ra == null && rb == null) return 0;
    if (ra == null) return 1;
    if (rb == null) return -1;
    return ra - rb;
  });
});
</script>
