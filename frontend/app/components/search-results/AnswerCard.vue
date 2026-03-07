<template>
  <ResultCard :result-data="resultData" card-type="Answers">
    <div class="flex flex-col gap-0">
      <DetailRow :label="getLabel('Question')">
        <div
          :class="computeTextClasses('Question', config.valueClassMap.Question)"
        >
          {{ getValue("Question") }}
        </div>
      </DetailRow>

      <DetailRow :label="getLabel('Answer')">
        <div
          :class="
            computeTextClasses(
              'Answer',
              config.getAnswerClass(resultData.Answer as string),
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

      <DetailRow
        v-if="hasMoreInformation"
        :label="getLabel('More Information')"
      >
        <div class="prose mb-2 flex flex-col gap-2">
          <div v-if="resultData['More Information']">
            {{ getValue("More Information") }}
          </div>
          <div v-else-if="resultData['OUP Book Quote']">
            {{ getValue("OUP Book Quote") }}
          </div>
          <template v-if="hasDomesticValue">
            <template v-if="resultData['Domestic Legal Provisions']">
              <LegalProvisionRenderer
                :value="String(getValue('Domestic Legal Provisions') ?? '')"
              />
            </template>
            <template v-else-if="resultData['Domestic Instruments ID']">
              <LegalProvisionRenderer
                skip-article
                :value="String(getValue('Domestic Instruments ID') ?? '')"
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
              resultData['Last Modified'] ? 'Last Modified' : 'Created',
              config.valueClassMap['Last Modified'],
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
  const value = props.resultData["Answer"];
  if (typeof value === "string" && value.includes(",")) {
    return value.split(",").map((part) => part.trim());
  }
  return getValue("Answer");
});

const literatureIdStr = computed(() => {
  const raw = props.resultData["Literature"];
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
  const links = props.resultData["Court Decisions Link"];
  if (!links || typeof links !== "string") return 0;
  return links.split(",").filter((link: string) => link.trim() !== "").length;
});

const relatedDecisionsLink = computed(() => {
  const id = props.resultData["id"];
  return `question/${id}#related-court-decisions`;
});

const hasDomesticValue = computed(() => {
  return !!(
    props.resultData["Domestic Legal Provisions"] ||
    props.resultData["Domestic Instruments ID"] ||
    props.resultData["Literature"]
  );
});

const hasMoreInformation = computed(() => {
  return (
    (props.resultData["More Information"] &&
      props.resultData["More Information"] !== "") ||
    (props.resultData["OUP Book Quote"] &&
      props.resultData["OUP Book Quote"] !== "") ||
    hasDomesticValue.value ||
    relatedCasesCount.value > 0
  );
});

const lastUpdatedDisplay = computed(() => {
  const raw = props.resultData["Last Modified"] || props.resultData["Created"];
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
