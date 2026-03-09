<template>
  <ResultCard :result-data="resultData" card-type="Answers">
    <div class="flex w-full flex-col gap-0">
      <DetailRow :label="getLabel('question')">
        <div
          :class="computeTextClasses('question', config.valueClassMap.question)"
        >
          {{ getValue("question") }}
        </div>
      </DetailRow>

      <DetailRow :label="getLabel('answer')">
        <div
          :class="
            computeTextClasses(
              'answer',
              config.getAnswerClass(resultData.answer as string),
            )
          "
        >
          <template v-if="Array.isArray(answerValue)">
            <div class="flex flex-col gap-2">
              <div v-for="(line, i) in answerValue" :key="i">
                {{ line }}
              </div>
            </div>
          </template>
          <template v-else>
            {{ answerValue }}
          </template>
        </div>
      </DetailRow>

      <DetailRow v-if="hasMoreInformation" :label="getLabel('moreInformation')">
        <div class="prose mb-2 flex flex-col gap-2">
          <div v-if="resultData.moreInformation">
            {{ getValue("moreInformation") }}
          </div>
          <div v-else-if="resultData.oupBookQuote">
            {{ getValue("oupBookQuote") }}
          </div>
          <div v-if="relatedCasesCount">
            <NuxtLink class="text-cold-purple" :to="relatedDecisionsLink">
              {{ relatedCasesCount }} related court decisions
            </NuxtLink>
          </div>
        </div>
      </DetailRow>

      <DetailRow v-if="lastUpdatedDisplay" label="Last Updated">
        <div
          :class="
            computeTextClasses(
              resultData.lastModified ? 'lastModified' : 'created',
              config.valueClassMap.lastModified,
            )
          "
        >
          {{ lastUpdatedDisplay }}
        </div>
      </DetailRow>
    </div>
  </ResultCard>
</template>

<script setup lang="ts">
import { computed } from "vue";
import ResultCard from "@/components/search-results/ResultCard.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import { answerCardConfig } from "@/config/cardConfigs";
import { formatYear } from "@/utils/format";
import { useCardFields } from "@/composables/useCardFields";

const props = defineProps<{
  resultData: Record<string, unknown>;
}>();

const config = answerCardConfig;

const { getLabel, getValue, computeTextClasses } = useCardFields(
  config,
  props.resultData,
);

const answerValue = computed(() => {
  const value = props.resultData.answer;
  if (typeof value === "string" && value.includes(",")) {
    return value.split(",").map((part) => part.trim());
  }
  return getValue("answer");
});

const relatedCasesCount = computed(() => {
  const links = props.resultData.courtDecisionsLink;
  if (!links || typeof links !== "string") return 0;
  return links.split(",").filter((link: string) => link.trim() !== "").length;
});

const relatedDecisionsLink = computed(() => {
  const id = props.resultData["id"];
  return `question/${id}#related-court-decisions`;
});

const hasMoreInformation = computed(() => {
  return (
    (props.resultData.moreInformation &&
      props.resultData.moreInformation !== "") ||
    (props.resultData.oupBookQuote && props.resultData.oupBookQuote !== "") ||
    relatedCasesCount.value > 0
  );
});

const lastUpdatedDisplay = computed(() => {
  const raw = props.resultData.lastModified || props.resultData.created;
  const y = formatYear(raw as string | null | undefined);
  return y ? String(y) : "";
});
</script>
