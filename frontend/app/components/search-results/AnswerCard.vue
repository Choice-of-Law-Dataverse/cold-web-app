<template>
  <ResultCard :result-data="resultData" card-type="Answers">
    <div class="flex flex-col gap-0">
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
          <template v-if="hasDomesticValue">
            <template v-if="resultData.domesticLegalProvisions">
              <LegalProvisionRenderer
                :value="String(getValue('domesticLegalProvisions') ?? '')"
              />
            </template>
            <template v-else-if="resultData.domesticInstrumentsId">
              <LegalProvisionRenderer
                skip-article
                :value="String(getValue('domesticInstrumentsId') ?? '')"
              />
            </template>
            <template v-else>
              <div v-if="literatureLoading">
                <LoadingBar class="pt-[11px]" />
              </div>
              <template v-else>
                <template v-if="literatureItems.length > 0">
                  <div v-for="item in literatureItems" :key="item.id">
                    <NuxtLink
                      class="text-cold-purple"
                      :to="`/literature/L-${item.id}`"
                      >{{ item.title }}</NuxtLink
                    >
                  </div>
                </template>
                <div v-else>
                  {{ getValue("Literature") }}
                </div>
              </template>
            </template>
          </template>
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
import LoadingBar from "@/components/layout/LoadingBar.vue";
import LegalProvisionRenderer from "@/components/legal/LegalProvisionRenderer.vue";
import { formatYear } from "@/utils/format";
import { useCardFields } from "@/composables/useCardFields";
import { useRecordDetailsList } from "@/composables/useRecordDetails";

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

const literatureIdStr = computed(() => {
  const raw = props.resultData.literature;
  return typeof raw === "string" ? raw : "";
});

const literatureIds = computed(() =>
  literatureIdStr.value
    ? literatureIdStr.value
        .split(",")
        .map((id: string) => id.trim())
        .filter((id: string) => id)
    : [],
);

const { data: literatureData, isLoading: literatureLoading } =
  useRecordDetailsList("Literature", literatureIds);

const literatureItems = computed(() => {
  if (!literatureData.value) return [];
  return literatureIds.value
    .map((id, i) => {
      const record = literatureData.value[i];
      const title = record?.Title;
      const finalTitle = title && title !== "NA" ? title : id;
      return { id, title: finalTitle as string };
    })
    .filter((item) => item.title);
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

const hasDomesticValue = computed(() => {
  return !!(
    props.resultData.domesticLegalProvisions ||
    props.resultData.domesticInstrumentsId ||
    props.resultData.literature
  );
});

const hasMoreInformation = computed(() => {
  return (
    (props.resultData.moreInformation &&
      props.resultData.moreInformation !== "") ||
    (props.resultData.oupBookQuote && props.resultData.oupBookQuote !== "") ||
    hasDomesticValue.value ||
    relatedCasesCount.value > 0
  );
});

const lastUpdatedDisplay = computed(() => {
  const raw = props.resultData.lastModified || props.resultData.created;
  const y = formatYear(raw as string | null | undefined);
  return y ? String(y) : "";
});
</script>

<style scoped>
.result-value-small li {
  list-style-type: disc;
  margin-left: 20px;
}
</style>
