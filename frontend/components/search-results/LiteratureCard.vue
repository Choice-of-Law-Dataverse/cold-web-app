<template>
  <ResultCard :result-data="processedResultData" card-type="Literature">
    <div class="flex flex-col gap-0">
      <!-- Title section -->
      <div class="flex flex-col md:flex-row md:items-start md:gap-6">
        <div class="label-key mt-0 md:mt-1 md:w-48 md:flex-shrink-0">
          {{ getLabel("Title") }}
        </div>
        <div
          :class="[
            config.valueClassMap.Title,
            'whitespace-pre-line text-sm leading-relaxed md:flex-1',
            (!processedResultData.Title ||
              processedResultData.Title === 'NA') &&
            config.keyLabelPairs.find((pair) => pair.key === 'Title')
              ?.emptyValueBehavior?.action === 'display'
              ? 'text-gray-300'
              : '',
          ]"
        >
          {{ getValue("Title") }}
        </div>
      </div>

      <!-- Author section -->
      <div class="flex flex-col md:flex-row md:items-start md:gap-6">
        <div class="label-key mt-0 md:mt-1 md:w-48 md:flex-shrink-0">
          {{ getLabel("Author") }}
        </div>
        <div
          :class="[
            config.valueClassMap.Author,
            'whitespace-pre-line text-sm leading-relaxed md:flex-1',
            (!processedResultData.Author ||
              processedResultData.Author === 'NA') &&
            config.keyLabelPairs.find((pair) => pair.key === 'Author')
              ?.emptyValueBehavior?.action === 'display'
              ? 'text-gray-300'
              : '',
          ]"
        >
          {{ getValue("Author") }}
        </div>
      </div>

      <!-- Publication Year section -->
      <div class="flex flex-col md:flex-row md:items-start md:gap-6">
        <div class="label-key mt-0 md:mt-1 md:w-48 md:flex-shrink-0">
          {{ getLabel("Publication Year") }}
        </div>
        <div
          :class="[
            config.valueClassMap['Publication Year'],
            'whitespace-pre-line text-sm leading-relaxed md:flex-1',
            (!processedResultData['Publication Year'] ||
              processedResultData['Publication Year'] === 'NA') &&
            config.keyLabelPairs.find((pair) => pair.key === 'Publication Year')
              ?.emptyValueBehavior?.action === 'display'
              ? 'text-gray-300'
              : '',
          ]"
        >
          {{ getValue("Publication Year") }}
        </div>
      </div>

      <!-- Publication Title section -->
      <template
        v-if="
          shouldDisplay('Publication Title') &&
          processedResultData['Publication Title']
        "
      >
        <div class="flex flex-col md:flex-row md:items-start md:gap-6">
          <div class="label-key mt-0 md:mt-1 md:w-48 md:flex-shrink-0">
            {{ getLabel("Publication Title") }}
          </div>
          <div
            :class="[
              config.valueClassMap['Publication Title'],
              'whitespace-pre-line text-sm leading-relaxed md:flex-1',
              (!processedResultData['Publication Title'] ||
                processedResultData['Publication Title'] === 'NA') &&
              config.keyLabelPairs.find(
                (pair) => pair.key === 'Publication Title',
              )?.emptyValueBehavior?.action === 'display'
                ? 'text-gray-300'
                : '',
            ]"
          >
            {{ getValue("Publication Title") }}
          </div>
        </div>
      </template>

      <!-- Publisher section -->
      <template
        v-else-if="
          shouldDisplay('Publisher') && processedResultData['Publisher']
        "
      >
        <div class="flex flex-col md:flex-row md:items-start md:gap-6">
          <div class="label-key mt-0 md:mt-1 md:w-48 md:flex-shrink-0">
            {{ getLabel("Publisher") }}
          </div>
          <div
            :class="[
              config.valueClassMap['Publisher'],
              'whitespace-pre-line text-sm leading-relaxed md:flex-1',
              (!processedResultData['Publisher'] ||
                processedResultData['Publisher'] === 'NA') &&
              config.keyLabelPairs.find((pair) => pair.key === 'Publisher')
                ?.emptyValueBehavior?.action === 'display'
                ? 'text-gray-300'
                : '',
            ]"
          >
            {{ getValue("Publisher") }}
          </div>
        </div>
      </template>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed } from "vue";
import ResultCard from "@/components/search-results/ResultCard.vue";
import { literatureCardConfig } from "@/config/cardConfigs";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const config = literatureCardConfig;

// Process the result data using the config's processData function
const processedResultData = computed(() => {
  return config.processData(props.resultData);
});

// Helper functions to get labels and values with fallbacks
const getLabel = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key);
  return pair?.label || key;
};

const shouldDisplay = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key);
  if (!pair?.emptyValueBehavior?.shouldDisplay) return true;
  return pair.emptyValueBehavior.shouldDisplay(processedResultData.value);
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
.literature-card-grid {
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
