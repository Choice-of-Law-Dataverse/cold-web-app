<template>
  <ResultCard
    :result-data="processedData ?? {}"
    card-type="Regional Instrument"
  >
    <div class="flex w-full flex-col gap-0">
      <DetailRow :label="getLabel('Abbreviation')">
        <TitleWithActions :title-class="fieldClasses('Abbreviation')">
          {{ getValue("Abbreviation") }}
          <template #actions>
            <PdfLink
              :pdf-field="resultData['Attachment']"
              :record-id="resultData.id"
              folder-name="regional-instruments"
            />
          </template>
        </TitleWithActions>
      </DetailRow>

      <DetailRow v-if="shouldDisplay('Date')" :label="getLabel('Date')">
        <div :class="fieldClasses('Date')">
          {{ format.formatDate(getValue("Date") as string) }}
        </div>
      </DetailRow>

      <DetailRow v-if="shouldDisplay('Title')" :label="getLabel('Title')">
        <div :class="fieldClasses('Title')">
          {{ getValue("Title") }}
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
import { regionalInstrumentCardConfig } from "@/config/cardConfigs";
import * as format from "@/utils/format";
import { useCardFields } from "@/composables/useCardFields";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const { getLabel, getValue, shouldDisplay, fieldClasses, processedData } =
  useCardFields(regionalInstrumentCardConfig, props.resultData);
</script>
