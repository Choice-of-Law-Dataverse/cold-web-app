<template>
  <ResultCard :resultData="processedResultData" cardType="Regional Instrument">
    <div class="grid grid-cols-1 gap-6 md:grid-cols-12">
      <!-- Abbreviation section -->
      <div
        :class="[
          config.gridConfig.abbreviation.columnSpan,
          config.gridConfig.abbreviation.startColumn,
        ]"
      >
        <div class="label-key">{{ getLabel("Abbreviation") }}</div>
        <div
          :class="[
            config.valueClassMap['Abbreviation'],
            'whitespace-pre-line text-sm leading-relaxed',
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
      </div>

      <!-- Date section -->
      <template v-if="shouldDisplay('Date')">
        <div
          :class="[
            config.gridConfig.date.columnSpan,
            config.gridConfig.date.startColumn,
          ]"
        >
          <div class="label-key">{{ getLabel("Date") }}</div>
          <div :class="[config.valueClassMap['Date']]">
            {{ format.formatDate(getValue("Date")) }}
          </div>
        </div>
      </template>

      <!-- Title section -->
      <template v-if="shouldDisplay('Title')">
        <div
          :class="[
            config.gridConfig.title.columnSpan,
            config.gridConfig.title.startColumn,
          ]"
        >
          <div class="label-key">{{ getLabel("Title") }}</div>
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
        </div>
      </template>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed } from "vue";
import ResultCard from "@/components/search-results/ResultCard.vue";
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
  // If you have a processData function for regional instruments, use it here
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
