<template>
  <ResultCard
    :result-data="processedData ?? {}"
    card-type="Domestic Instrument"
  >
    <div class="flex w-full flex-col gap-0">
      <DetailRow :label="getLabel('titleInEnglish')">
        <TitleWithActions :title-class="fieldClasses('titleInEnglish')">
          {{ getValue("titleInEnglish") }}
          <template #actions>
            <PdfLink
              :pdf-field="resultData.officialSourcePdf || resultData.sourcePdf"
              :record-id="resultData.id"
              folder-name="domestic-instruments"
            />
          </template>
        </TitleWithActions>
      </DetailRow>

      <DetailRow
        v-if="
          processedData && processedData.date && processedData.date !== 'NA'
        "
        :label="getLabel('date')"
      >
        <div :class="fieldClasses('date')">
          {{ getValue("date") }}
        </div>
      </DetailRow>

      <DetailRow
        v-if="
          processedData &&
          processedData.abbreviation &&
          processedData.abbreviation !== 'NA'
        "
        :label="getLabel('abbreviation')"
      >
        <div :class="fieldClasses('abbreviation')">
          {{ getValue("abbreviation") }}
        </div>
      </DetailRow>
    </div>
  </ResultCard>
</template>

<script setup lang="ts">
import ResultCard from "@/components/search-results/ResultCard.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import TitleWithActions from "@/components/ui/TitleWithActions.vue";
import { legislationCardConfig } from "@/config/cardConfigs";
import { useCardFields } from "@/composables/useCardFields";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const { getLabel, getValue, fieldClasses, processedData } = useCardFields(
  legislationCardConfig,
  props.resultData,
);
</script>
