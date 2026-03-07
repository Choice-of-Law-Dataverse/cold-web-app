<template>
  <ResultCard
    :result-data="processedData ?? {}"
    card-type="International Instrument"
  >
    <div class="flex w-full flex-col gap-0">
      <DetailRow :label="getLabel('name')">
        <TitleWithActions :title-class="fieldClasses('name')">
          {{ getValue("name") }}
          <template #actions>
            <PdfLink
              :pdf-field="
                resultData.officialSourcePdf ||
                resultData.sourcePdf ||
                resultData.attachment
              "
              :record-id="resultData.id"
              folder-name="international-instruments"
            />
          </template>
        </TitleWithActions>
      </DetailRow>

      <DetailRow v-if="shouldDisplay('date')" :label="getLabel('date')">
        <div :class="fieldClasses('date')">
          {{ format.formatDate(getValue("date") as string) }}
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
import { internationalInstrumentCardConfig } from "@/config/cardConfigs";
import * as format from "@/utils/format.js";
import { useCardFields } from "@/composables/useCardFields";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const { getLabel, getValue, shouldDisplay, fieldClasses, processedData } =
  useCardFields(internationalInstrumentCardConfig, props.resultData);
</script>
