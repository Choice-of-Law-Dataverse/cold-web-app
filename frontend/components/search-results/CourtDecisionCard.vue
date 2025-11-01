<template>
  <ResultCard :result-data="resultData" card-type="Court Decisions">
    <div class="flex flex-col gap-0">
      <!-- Case Title section -->
      <DetailRow :label="getLabel('Case Title')">
        <div class="flex items-start justify-between gap-4">
          <div
            :class="[
              config.valueClassMap['Case Title'],
              'flex-1 whitespace-pre-line text-sm leading-relaxed',
              (!resultData['Case Title'] ||
                resultData['Case Title'] === 'NA') &&
              config.keyLabelPairs.find((pair) => pair.key === 'Case Title')
                ?.emptyValueBehavior?.action === 'display' &&
              !config.keyLabelPairs.find((pair) => pair.key === 'Case Title')
                ?.emptyValueBehavior?.getFallback
                ? 'text-gray-300'
                : '',
            ]"
          >
            {{ getValue("Case Title") }}
          </div>

          <PdfLink :record-id="resultData.id" folder-name="court-decisions" />
        </div>
      </DetailRow>

      <!-- Date section -->
      <DetailRow
        v-if="
          resultData['Publication Date ISO'] &&
          resultData['Publication Date ISO'] !== 'NA'
        "
        :label="getLabel('Publication Date ISO')"
      >
        <div
          :class="[
            config.valueClassMap['Publication Date ISO'],
            'whitespace-pre-line text-sm leading-relaxed',
          ]"
        >
          {{ getValue("Publication Date ISO") }}
        </div>
      </DetailRow>

      <!-- Instance section -->
      <DetailRow
        v-if="resultData['Instance'] && resultData['Instance'] !== 'NA'"
        :label="getLabel('Instance')"
      >
        <div
          :class="[
            config.valueClassMap['Instance'],
            'whitespace-pre-line text-sm leading-relaxed',
          ]"
        >
          {{ getValue("Instance") }}
        </div>
      </DetailRow>

      <!-- Choice of Law Issue section -->
      <DetailRow
        v-if="
          resultData['Choice of Law Issue'] &&
          resultData['Choice of Law Issue'] !== 'NA'
        "
        :label="getLabel('Choice of Law Issue')"
      >
        <div
          :class="[
            config.valueClassMap['Choice of Law Issue'],
            'whitespace-pre-line text-sm leading-relaxed',
          ]"
        >
          {{ getValue("Choice of Law Issue") }}
        </div>
      </DetailRow>
    </div>
  </ResultCard>
</template>

<script setup>
import ResultCard from "@/components/search-results/ResultCard.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import { courtDecisionCardConfig } from "@/config/cardConfigs";
import { extractYear } from "@/utils/format";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const config = courtDecisionCardConfig;

const getLabel = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key);
  return pair?.label || key;
};

const getValue = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key);
  let value = props.resultData[key];

  if (key === "Publication Date ISO" && value && value !== "NA") {
    value = extractYear(value);
  }

  if ((!value || value === "NA") && pair?.emptyValueBehavior) {
    if (pair.emptyValueBehavior.action === "display") {
      if (pair.emptyValueBehavior.getFallback) {
        return pair.emptyValueBehavior.getFallback(props.resultData);
      }
      return pair.emptyValueBehavior.fallback;
    }
    return "";
  }

  return value;
};
</script>

<style scoped>
.court-decision-grid {
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
