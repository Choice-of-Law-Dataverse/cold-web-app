<template>
  <ResultCard
    :result-data="processedData ?? {}"
    card-type="Domestic Instrument"
  >
    <div class="flex w-full flex-col gap-0">
      <DetailRow :label="getLabel('Title (in English)')">
        <TitleWithActions :title-class="fieldClasses('Title (in English)')">
          {{ getValue("Title (in English)") }}
          <template #actions>
            <PdfLink
              :pdf-field="
                resultData['Official Source (PDF)'] ||
                resultData['Source (PDF)']
              "
              :record-id="resultData.id"
              folder-name="domestic-instruments"
            />
          </template>
        </TitleWithActions>
      </DetailRow>

      <DetailRow
        v-if="
          processedData &&
          processedData['Date'] &&
          processedData['Date'] !== 'NA'
        "
        :label="getLabel('Date')"
      >
        <div :class="fieldClasses('Date')">
          {{ getValue("Date") }}
        </div>
      </DetailRow>

      <DetailRow
        v-if="
          processedData &&
          processedData['Abbreviation'] &&
          processedData['Abbreviation'] !== 'NA'
        "
        :label="getLabel('Abbreviation')"
      >
        <div :class="fieldClasses('Abbreviation')">
          {{ getValue("Abbreviation") }}
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
