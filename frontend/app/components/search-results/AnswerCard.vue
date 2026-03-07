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
              config.getAnswerClass(resultData.answer),
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
                :value="getValue('domesticLegalProvisions')"
              />
            </template>
            <template v-else-if="resultData.domesticInstrumentsId">
              <LegalProvisionRenderer
                skip-article
                :value="getValue('domesticInstrumentsId')"
              />
            </template>
            <template v-else>
              <div v-if="isLoadingLiterature">
                <LoadingBar class="pt-[11px]" />
              </div>
              <template v-else>
                <template v-if="Array.isArray(domesticValue)">
                  <div v-for="(item, index) in domesticValue" :key="index">
                    <NuxtLink
                      class="text-cold-purple"
                      :to="`/literature/L-${item.id}`"
                      >{{ item.title }}</NuxtLink
                    >
                  </div>
                </template>
                <div v-else>
                  {{ domesticValue }}
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

<script setup>
import { computed, ref, watch } from "vue";
import ResultCard from "@/components/search-results/ResultCard.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import { answerCardConfig } from "@/config/cardConfigs";
import { literatureCache } from "@/utils/literatureCache";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import LegalProvisionRenderer from "@/components/legal/LegalProvisionRenderer.vue";
import { formatYear } from "@/utils/format";
import { useCardFields } from "@/composables/useCardFields";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

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

const literatureTitles = ref([]);

async function fetchLiteratureTitles(idStr) {
  const ids = idStr.split(",").map((id) => id.trim());
  const promises = ids.map(async (id) => {
    if (literatureCache[id]) return { id, title: literatureCache[id] };
    try {
      const response = await fetch(`/api/proxy/search/details`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ table: "Literature", id }),
      });
      if (!response.ok) throw new Error("Failed to fetch literature title");
      const data = await response.json();
      const title = data.title;
      const finalTitle = title && title !== "NA" ? title : id;
      literatureCache[id] = finalTitle;
      return { id, title: finalTitle };
    } catch (err) {
      console.error("Error fetching literature title:", err);
      return { id, title: id };
    }
  });
  literatureTitles.value = await Promise.all(promises);
}

watch(
  () => props.resultData.literature,
  (newId) => {
    if (newId) fetchLiteratureTitles(newId);
  },
  { immediate: true },
);

const domesticValue = computed(() => {
  if (props.resultData.domesticLegalProvisions != null) {
    return getValue("domesticLegalProvisions");
  } else if (props.resultData.domesticInstrumentsId != null) {
    return getValue("domesticInstrumentsId");
  } else if (props.resultData.literature != null) {
    return literatureTitles.value;
  } else {
    return "";
  }
});

const isLoadingLiterature = computed(() => {
  return (
    props.resultData.literature != null &&
    (!literatureTitles.value ||
      literatureTitles.value.length === 0 ||
      literatureTitles.value.includes(null))
  );
});

const relatedCasesCount = computed(() => {
  const links = props.resultData.courtDecisionsLink;
  if (!links) return 0;
  return links.split(",").filter((link) => link.trim() !== "").length;
});

const relatedDecisionsLink = computed(() => {
  const id = props.resultData["id"];
  return `question/${id}#related-court-decisions`;
});

const hasDomesticValue = computed(() => {
  return (
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
  const y = formatYear(raw);
  return y ? String(y) : "";
});
</script>

<style scoped>
.result-value-small li {
  list-style-type: disc;
  margin-left: 20px;
}
</style>
