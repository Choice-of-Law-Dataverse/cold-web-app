<template>
  <ResultCard :result-data="resultData" card-type="Court Decisions">
    <div class="flex w-full flex-col gap-0">
      <DetailRow :label="getLabel('caseTitle')">
        <TitleWithActions :title-class="fieldClasses('caseTitle')">
          {{ getValue("caseTitle") }}
          <template #actions>
            <PdfLink
              :pdf-field="resultData.officialSourcePdf || resultData.sourcePdf"
              :record-id="resultData.id"
              folder-name="court-decisions"
            />
          </template>
        </TitleWithActions>
      </DetailRow>

      <DetailRow
        v-if="
          resultData.publicationDateIso &&
          resultData.publicationDateIso !== 'NA'
        "
        :label="getLabel('publicationDateIso')"
      >
        <div :class="fieldClasses('publicationDateIso')">
          {{ extractYear(resultData.publicationDateIso) }}
        </div>
      </DetailRow>

      <DetailRow
        v-if="resultData.instance && resultData.instance !== 'NA'"
        :label="getLabel('instance')"
      >
        <div :class="fieldClasses('instance')">
          {{ getValue("instance") }}
        </div>
      </DetailRow>

      <DetailRow
        v-if="
          resultData.choiceOfLawIssue && resultData.choiceOfLawIssue !== 'NA'
        "
        :label="getLabel('choiceOfLawIssue')"
      >
        <div :class="fieldClasses('choiceOfLawIssue')">
          {{ getValue("choiceOfLawIssue") }}
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
