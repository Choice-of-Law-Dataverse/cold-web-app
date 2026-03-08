<template>
  <ResultCard :result-data="resultData" card-type="Arbitral Awards">
    <div class="flex w-full flex-col gap-0">
      <DetailRow
        v-if="
          resultData.arbitralInstitutions &&
          resultData.arbitralInstitutions !== 'NA'
        "
        :label="getLabel('arbitralInstitutions')"
      >
        <div :class="fieldClasses('arbitralInstitutions')">
          {{ getValue("arbitralInstitutions") }}
        </div>
      </DetailRow>

      <DetailRow
        v-if="resultData.awardSummary && resultData.awardSummary !== 'NA'"
        :label="getLabel('awardSummary')"
      >
        <div :class="fieldClasses('awardSummary')">
          {{ getValue("awardSummary") }}
        </div>
      </DetailRow>
    </div>
  </ResultCard>
</template>

<script setup lang="ts">
import ResultCard from "@/components/search-results/ResultCard.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import { arbitralAwardCardConfig } from "@/config/cardConfigs";
import { useCardFields } from "@/composables/useCardFields";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const { getLabel, getValue, fieldClasses } = useCardFields(
  arbitralAwardCardConfig,
  props.resultData,
);
</script>
