<template>
  <ResultCard :result-data="processedResultData" card-type="Literature">
    <div class="flex flex-col gap-0">
      <!-- Title section -->
      <DetailRow :label="getLabel('Title')">
        <div
          :class="[
            config.valueClassMap.Title,
            'text-sm leading-relaxed whitespace-pre-line',
            (!processedResultData.Title ||
              processedResultData.Title === 'NA') &&
            config.keyLabelPairs.find((pair) => pair.key === 'Title')
              ?.emptyValueBehavior?.action === 'display'
              ? 'text-gray-400'
              : '',
          ]"
        >
          {{ getValue("Title") }}
        </div>
      </DetailRow>

      <!-- Author section -->
      <DetailRow :label="getLabel('Author')">
        <div
          :class="[
            config.valueClassMap.Author,
            'text-sm leading-relaxed whitespace-pre-line',
            (!processedResultData.Author ||
              processedResultData.Author === 'NA') &&
            config.keyLabelPairs.find((pair) => pair.key === 'Author')
              ?.emptyValueBehavior?.action === 'display'
              ? 'text-gray-400'
              : '',
          ]"
        >
          {{ getValue("Author") }}
        </div>
      </DetailRow>

      <!-- Publication Year section -->
      <DetailRow :label="getLabel('Publication Year')">
        <div
          :class="[
            config.valueClassMap['Publication Year'],
            'text-sm leading-relaxed whitespace-pre-line',
            (!processedResultData['Publication Year'] ||
              processedResultData['Publication Year'] === 'NA') &&
            config.keyLabelPairs.find((pair) => pair.key === 'Publication Year')
              ?.emptyValueBehavior?.action === 'display'
              ? 'text-gray-400'
              : '',
          ]"
        >
          {{ getValue("Publication Year") }}
        </div>
      </DetailRow>

      <!-- Publication Title section -->
      <template
        v-if="
          shouldDisplay('Publication Title') &&
          processedResultData['Publication Title']
        "
      >
        <DetailRow :label="getLabel('Publication Title')">
          <div
            :class="[
              config.valueClassMap['Publication Title'],
              'text-sm leading-relaxed whitespace-pre-line',
              (!processedResultData['Publication Title'] ||
                processedResultData['Publication Title'] === 'NA') &&
              config.keyLabelPairs.find(
                (pair) => pair.key === 'Publication Title',
              )?.emptyValueBehavior?.action === 'display'
                ? 'text-gray-400'
                : '',
            ]"
          >
            {{ getValue("Publication Title") }}
          </div>
        </DetailRow>
      </template>

      <!-- Publisher section -->
      <template
        v-else-if="
          shouldDisplay('Publisher') && processedResultData['Publisher']
        "
      >
        <DetailRow :label="getLabel('Publisher')">
          <div
            :class="[
              config.valueClassMap['Publisher'],
              'text-sm leading-relaxed whitespace-pre-line',
              (!processedResultData['Publisher'] ||
                processedResultData['Publisher'] === 'NA') &&
              config.keyLabelPairs.find((pair) => pair.key === 'Publisher')
                ?.emptyValueBehavior?.action === 'display'
                ? 'text-gray-400'
                : '',
            ]"
          >
            {{ getValue("Publisher") }}
          </div>
        </DetailRow>
      </template>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed } from "vue";
import ResultCard from "@/components/search-results/ResultCard.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import { literatureCardConfig } from "@/config/cardConfigs";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const config = literatureCardConfig;

const processedResultData = computed(() => {
  return config.processData(props.resultData);
});

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
</style>
