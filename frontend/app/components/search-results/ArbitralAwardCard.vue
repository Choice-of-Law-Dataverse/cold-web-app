<template>
  <ResultCard :result-data="resultData" card-type="Arbitral Awards">
    <div class="flex w-full flex-col gap-0">
      <DetailRow :label="getLabel('caseNumber')">
        <div :class="fieldClasses('caseNumber')">
          {{ getValue("caseNumber") }}
        </div>
      </DetailRow>

      <DetailRow
        v-if="resultData.year && resultData.year !== 'NA'"
        :label="getLabel('year')"
      >
        <div :class="fieldClasses('year')">
          {{ getValue("year") }}
        </div>
      </DetailRow>

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
        v-if="
          resultData.natureOfTheAward && resultData.natureOfTheAward !== 'NA'
        "
        :label="getLabel('natureOfTheAward')"
      >
        <div :class="fieldClasses('natureOfTheAward')">
          {{ getValue("natureOfTheAward") }}
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
