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
              config.getAnswerClass(resultData.Answer),
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
                :value="getValue('Domestic Legal Provisions')"
              />
            </template>
            <template v-else-if="resultData['Domestic Instruments ID']">
              <LegalProvisionRenderer
                skip-article
                :value="getValue('Domestic Instruments ID')"
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
  const value = props.resultData["Answer"];
  if (typeof value === "string" && value.includes(",")) {
    return value.split(",").map((part) => part.trim());
  }
  return getValue("Answer");
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
      const title = data["Title"];
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
  () => props.resultData["Literature"],
  (newId) => {
    if (newId) fetchLiteratureTitles(newId);
  },
  { immediate: true },
);

const domesticValue = computed(() => {
  if (props.resultData["Domestic Legal Provisions"] != null) {
    return getValue("Domestic Legal Provisions");
  } else if (props.resultData["Domestic Instruments ID"] != null) {
    return getValue("Domestic Instruments ID");
  } else if (props.resultData["Literature"] != null) {
    return literatureTitles.value;
  } else {
    return "";
  }
});

const isLoadingLiterature = computed(() => {
  return (
    props.resultData["Literature"] != null &&
    (!literatureTitles.value ||
      literatureTitles.value.length === 0 ||
      literatureTitles.value.includes(null))
  );
});

const relatedCasesCount = computed(() => {
  const links = props.resultData["Court Decisions Link"];
  if (!links) return 0;
  return links.split(",").filter((link) => link.trim() !== "").length;
});

const relatedDecisionsLink = computed(() => {
  const id = props.resultData["id"];
  return `question/${id}#related-court-decisions`;
});

const hasDomesticValue = computed(() => {
  return (
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
