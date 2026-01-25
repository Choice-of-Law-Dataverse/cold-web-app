<template>
  <ResultCard
    :result-data="processedResultData"
    card-type="International Instrument"
  >
    <div class="flex w-full flex-col gap-0">
      <!-- Title section -->
      <DetailRow :label="getLabel('Name')">
        <div class="flex w-full items-start justify-between gap-4">
          <div
            :class="[
              config.valueClassMap['Name'],
              'text-sm leading-relaxed whitespace-pre-line',
              (!processedResultData['Name'] ||
                processedResultData['Name'] === 'NA') &&
              config.keyLabelPairs.find((pair) => pair.key === 'Name')
                ?.emptyValueBehavior?.action === 'display'
                ? 'text-gray-400'
                : '',
            ]"
          >
            {{ getValue("Name") }}
          </div>

          <PdfLink
            :pdf-field="
              resultData['Official Source (PDF)'] ||
              resultData['Source (PDF)'] ||
              resultData['Attachment']
            "
            :record-id="resultData.id"
            folder-name="international-instruments"
          />
        </div>
      </DetailRow>

      <!-- Date section -->
      <DetailRow v-if="shouldDisplay('Date')" :label="getLabel('Date')">
        <div :class="config.valueClassMap['Date']">
          {{ format.formatDate(getValue("Date")) }}
        </div>
      </DetailRow>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed } from "vue";
import ResultCard from "@/components/search-results/ResultCard.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import { internationalInstrumentCardConfig } from "@/config/cardConfigs";
import * as format from "@/utils/format.js";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const config = internationalInstrumentCardConfig;

const processedResultData = computed(() => {
  return props.resultData;
});

const getLabel = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key);
  return pair?.label || key;
};

const getValue = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key);
  const value = processedResultData.value?.[key];
  if (!value && pair?.emptyValueBehavior) {
    if (pair.emptyValueBehavior.action === "display") {
      return pair.emptyValueBehavior.fallback;
    }
    return "";
  }
  return value;
};

const shouldDisplay = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key);
  return (
    pair?.emptyValueBehavior?.action === "display" ||
    processedResultData.value?.[key]
  );
};
</script>

<style scoped>
.legislation-card-grid {
  display: grid;
  grid-template-columns: repeat(12, var(--column-width));
  column-gap: var(--gutter-width);
  align-items: start;
}

.grid-item {
  display: flex;
  flex-direction: column;
}
</style>
