<template>
  <ResultCard
    :result-data="processedResultData"
    card-type="Domestic Instrument"
  >
    <div class="flex flex-col gap-0">
      <!-- Title section -->
      <DetailRow :label="getLabel('Title (in English)')">
        <div class="flex items-start justify-between gap-4">
          <div
            :class="[
              config.valueClassMap['Title (in English)'],
              'flex-1 whitespace-pre-line text-sm leading-relaxed',
              (!processedResultData['Title (in English)'] ||
                processedResultData['Title (in English)'] === 'NA') &&
              config.keyLabelPairs.find(
                (pair) => pair.key === 'Title (in English)',
              )?.emptyValueBehavior?.action === 'display'
                ? 'text-gray-400'
                : '',
            ]"
          >
            {{ getValue("Title (in English)") }}
          </div>

          <PdfLink
            :record-id="resultData.id"
            folder-name="domestic-instruments"
          />
        </div>
      </DetailRow>

      <!-- Date section -->
      <DetailRow
        v-if="
          processedResultData &&
          processedResultData['Date'] &&
          processedResultData['Date'] !== 'NA'
        "
        :label="getLabel('Date')"
      >
        <div
          :class="[
            config.valueClassMap['Date'],
            'whitespace-pre-line text-sm leading-relaxed',
          ]"
        >
          {{ getValue("Date") }}
        </div>
      </DetailRow>

      <!-- Abbreviation section -->
      <DetailRow
        v-if="
          processedResultData &&
          processedResultData['Abbreviation'] &&
          processedResultData['Abbreviation'] !== 'NA'
        "
        :label="getLabel('Abbreviation')"
      >
        <div
          :class="[
            config.valueClassMap['Abbreviation'],
            'whitespace-pre-line text-sm leading-relaxed',
          ]"
        >
          {{ getValue("Abbreviation") }}
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
import { legislationCardConfig } from "@/config/cardConfigs";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const config = legislationCardConfig;

const processedResultData = computed(() => {
  return config.processData(props.resultData);
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
