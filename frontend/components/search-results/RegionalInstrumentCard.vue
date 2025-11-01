<template>
  <ResultCard
    :result-data="processedResultData"
    card-type="Regional Instrument"
  >
    <div class="flex flex-col gap-0">
      <!-- Abbreviation section -->
      <TwoColumnLayout :label="getLabel('Abbreviation')">
        <div class="flex items-start justify-between gap-4">
          <div
            :class="[
              config.valueClassMap['Abbreviation'],
              'flex-1 whitespace-pre-line text-sm leading-relaxed',
              (!processedResultData['Abbreviation'] ||
                processedResultData['Abbreviation'] === 'NA') &&
              config.keyLabelPairs.find((pair) => pair.key === 'Abbreviation')
                ?.emptyValueBehavior?.action === 'display'
                ? 'text-gray-300'
                : '',
            ]"
          >
            {{ getValue("Abbreviation") }}
          </div>

          <PdfLink
            :record-id="resultData.id"
            folder-name="regional-instruments"
          />
        </div>
      </TwoColumnLayout>

      <!-- Date section -->
      <TwoColumnLayout v-if="shouldDisplay('Date')" :label="getLabel('Date')">
        <div :class="config.valueClassMap['Date']">
          {{ format.formatDate(getValue("Date")) }}
        </div>
      </TwoColumnLayout>

      <!-- Title section -->
      <TwoColumnLayout v-if="shouldDisplay('Title')" :label="getLabel('Title')">
        <div
          :class="[
            config.valueClassMap['Title'],
            'whitespace-pre-line text-sm leading-relaxed',
            (!processedResultData['Title'] ||
              processedResultData['Title'] === 'NA') &&
            config.keyLabelPairs.find((pair) => pair.key === 'Title')
              ?.emptyValueBehavior?.action === 'display'
              ? 'text-gray-300'
              : '',
          ]"
        >
          {{ getValue("Title") }}
        </div>
      </TwoColumnLayout>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed } from "vue";
import ResultCard from "@/components/search-results/ResultCard.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import TwoColumnLayout from "@/components/ui/TwoColumnLayout.vue";
import { regionalInstrumentCardConfig } from "@/config/cardConfigs";
import * as format from "@/utils/format";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const config = regionalInstrumentCardConfig;

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
