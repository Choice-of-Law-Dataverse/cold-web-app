<template>
  <ResultCard
    :result-data="processedResultData"
    card-type="International Instrument"
  >
    <div class="flex flex-col gap-0">
      <!-- Title section -->
      <div class="flex flex-col md:flex-row md:items-start md:gap-6">
        <div class="label-key mt-0 md:mt-1 md:w-48 md:flex-shrink-0">
          {{ getLabel("Name") }}
        </div>
        <div class="flex items-start justify-between gap-4 md:flex-1">
          <div
            :class="[
              config.valueClassMap['Name'],
              'whitespace-pre-line text-sm leading-relaxed flex-1',
              (!processedResultData['Name'] ||
                processedResultData['Name'] === 'NA') &&
              config.keyLabelPairs.find((pair) => pair.key === 'Name')
                ?.emptyValueBehavior?.action === 'display'
                ? 'text-gray-300'
                : '',
            ]"
          >
            {{ getValue("Name") }}
          </div>
          
          <PdfLink :record-id="resultData.id" folder-name="international-instruments" />
        </div>
      </div>

      <!-- Date section -->
      <template v-if="shouldDisplay('Date')">
        <div class="flex flex-col md:flex-row md:items-start md:gap-6">
          <div class="label-key mt-0 md:mt-1 md:w-48 md:flex-shrink-0">
            {{ getLabel("Date") }}
          </div>
          <div :class="[config.valueClassMap['Date'], 'md:flex-1']">
            {{ format.formatDate(getValue("Date")) }}
          </div>
        </div>
      </template>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed } from "vue";
import ResultCard from "@/components/search-results/ResultCard.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
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
  // If you have a processData function for international instruments, use it here
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

.label-key {
  @extend .label;
  padding: 0;
  margin-top: 12px;
}
</style>
