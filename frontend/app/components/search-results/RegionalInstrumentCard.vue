<template>
  <ResultCard
    :result-data="processedData ?? {}"
    card-type="Regional Instrument"
  >
    <div class="flex w-full flex-col gap-0">
      <DetailRow :label="getLabel('abbreviation')">
        <TitleWithActions :title-class="fieldClasses('abbreviation')">
          {{ getValue("abbreviation") }}
          <template #actions>
            <PdfLink
              :pdf-field="resultData.attachment"
              :record-id="resultData.id"
              folder-name="regional-instruments"
            />
          </template>
        </TitleWithActions>
      </DetailRow>

      <DetailRow v-if="shouldDisplay('date')" :label="getLabel('date')">
        <div :class="fieldClasses('date')">
          {{ format.formatDate(getValue("date") as string) }}
        </div>
      </DetailRow>

      <DetailRow v-if="shouldDisplay('title')" :label="getLabel('title')">
        <div :class="fieldClasses('title')">
          {{ getValue("title") }}
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
