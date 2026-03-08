<template>
  <ResultCard :result-data="resultData" card-type="Arbitral Rules">
    <div class="flex w-full flex-col gap-0">
      <DetailRow :label="getLabel('setOfRules')">
        <div :class="fieldClasses('setOfRules')">
          {{ getValue("setOfRules") }}
        </div>
      </DetailRow>

      <DetailRow
        v-if="resultData.inForceFrom && resultData.inForceFrom !== 'NA'"
        :label="getLabel('inForceFrom')"
      >
        <div :class="fieldClasses('inForceFrom')">
          {{ getValue("inForceFrom") }}
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
    </div>
  </ResultCard>
</template>

<script setup lang="ts">
import ResultCard from "@/components/search-results/ResultCard.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import { arbitralRuleCardConfig } from "@/config/cardConfigs";
import { useCardFields } from "@/composables/useCardFields";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const { getLabel, getValue, fieldClasses } = useCardFields(
  arbitralRuleCardConfig,
  props.resultData,
);
</script>
