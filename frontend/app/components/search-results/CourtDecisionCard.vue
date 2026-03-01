<template>
  <ResultCard :result-data="resultData" card-type="Court Decisions">
    <div class="flex w-full flex-col gap-0">
      <DetailRow :label="getLabel('Case Title')">
        <TitleWithActions :title-class="fieldClasses('Case Title')">
          {{ getValue("Case Title") }}
          <template #actions>
            <PdfLink
              :pdf-field="
                resultData['Official Source (PDF)'] ||
                resultData['Source (PDF)']
              "
              :record-id="resultData.id"
              folder-name="court-decisions"
            />
          </template>
        </TitleWithActions>
      </DetailRow>

      <DetailRow
        v-if="
          resultData['Publication Date ISO'] &&
          resultData['Publication Date ISO'] !== 'NA'
        "
        :label="getLabel('Publication Date ISO')"
      >
        <div :class="fieldClasses('Publication Date ISO')">
          {{ extractYear(resultData["Publication Date ISO"]) }}
        </div>
      </DetailRow>

      <DetailRow
        v-if="resultData['Instance'] && resultData['Instance'] !== 'NA'"
        :label="getLabel('Instance')"
      >
        <div :class="fieldClasses('Instance')">
          {{ getValue("Instance") }}
        </div>
      </DetailRow>

      <DetailRow
        v-if="
          resultData['Choice of Law Issue'] &&
          resultData['Choice of Law Issue'] !== 'NA'
        "
        :label="getLabel('Choice of Law Issue')"
      >
        <div :class="fieldClasses('Choice of Law Issue')">
          {{ getValue("Choice of Law Issue") }}
        </div>
      </DetailRow>
    </div>
  </ResultCard>
</template>

<script setup lang="ts">
import ResultCard from "@/components/search-results/ResultCard.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import TitleWithActions from "@/components/ui/TitleWithActions.vue";
import { courtDecisionCardConfig } from "@/config/cardConfigs";
import { extractYear } from "@/utils/format";
import { useCardFields } from "@/composables/useCardFields";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const { getLabel, getValue, fieldClasses } = useCardFields(
  courtDecisionCardConfig,
  props.resultData,
);
</script>
