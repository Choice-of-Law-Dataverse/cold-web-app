<template>
  <ResultCard
    :result-data="processedResultData"
    card-type="Domestic Instrument"
  >
    <div class="flex flex-col gap-0">
      <!-- Title section -->
      <div class="flex flex-col md:flex-row md:gap-6 md:items-start">
        <div class="label-key md:w-48 md:flex-shrink-0 mt-0 md:mt-1">
          {{ getLabel("Title (in English)") }}
        </div>
        <div
          :class="[
            config.valueClassMap['Title (in English)'],
            'whitespace-pre-line text-sm leading-relaxed md:flex-1',
            (!processedResultData['Title (in English)'] ||
              processedResultData['Title (in English)'] === 'NA') &&
            config.keyLabelPairs.find(
              (pair) => pair.key === 'Title (in English)',
            )?.emptyValueBehavior?.action === 'display'
              ? 'text-gray-300'
              : '',
          ]"
        >
          {{ getValue("Title (in English)") }}
        </div>
      </div>

      <!-- Date section -->
      <div
        v-if="
          processedResultData &&
          processedResultData['Date'] &&
          processedResultData['Date'] !== 'NA'
        "
        class="flex flex-col md:flex-row md:gap-6 md:items-start"
      >
        <div class="label-key md:w-48 md:flex-shrink-0 mt-0 md:mt-1">
          {{ getLabel("Date") }}
        </div>
        <div
          :class="[
            config.valueClassMap['Date'],
            'whitespace-pre-line text-sm leading-relaxed md:flex-1',
          ]"
        >
          {{ getValue("Date") }}
        </div>
      </div>

      <!-- Abbreviation section -->
      <div
        v-if="
          processedResultData &&
          processedResultData['Abbreviation'] &&
          processedResultData['Abbreviation'] !== 'NA'
        "
        class="flex flex-col md:flex-row md:gap-6 md:items-start"
      >
        <div class="label-key md:w-48 md:flex-shrink-0 mt-0 md:mt-1">
          {{ getLabel("Abbreviation") }}
        </div>
        <div
          :class="[
            config.valueClassMap['Abbreviation'],
            'whitespace-pre-line text-sm leading-relaxed md:flex-1',
          ]"
        >
          {{ getValue("Abbreviation") }}
        </div>
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed } from "vue";
import ResultCard from "@/components/search-results/ResultCard.vue";
import { legislationCardConfig } from "@/config/cardConfigs";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const config = legislationCardConfig;

// Process the result data using the config's processData function
const processedResultData = computed(() => {
  return config.processData(props.resultData);
});

// Helper functions to get labels and values with fallbacks
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
