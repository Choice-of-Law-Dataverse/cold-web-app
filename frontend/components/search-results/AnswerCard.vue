<template>
  <ResultCard :result-data="resultData" card-type="Answers">
    <div class="grid grid-cols-1 gap-6 md:grid-cols-12">
      <!-- Question section -->
      <div
        :class="[
          config.gridConfig.question.columnSpan,
          config.gridConfig.question.startColumn,
        ]"
      >
        <div class="label label-key">{{ getLabel("Question") }}</div>
        <div
          :class="computeTextClasses('Question', config.valueClassMap.Question)"
        >
          {{ getValue("Question") }}
        </div>
      </div>

      <!-- Answer section -->
      <div
        :class="[
          config.gridConfig.answer.columnSpan,
          config.gridConfig.answer.startColumn,
        ]"
      >
        <div class="label label-key">{{ getLabel("Answer") }}</div>
        <div
          :class="
            computeTextClasses(
              'Answer',
              config.getAnswerClass(resultData.Answer),
            )
          "
        >
          <template v-if="Array.isArray(getValue('Answer'))">
            <ul class="list-disc pl-5">
              <li v-for="(line, i) in getValue('Answer')" :key="i">
                {{ line }}
              </li>
            </ul>
          </template>
          <template v-else>
            {{ getValue("Answer") }}
          </template>
        </div>

        <!-- Last Modified (inline under Answer), fallback to Created when absent -->
        <div v-if="lastUpdatedDisplay" class="mt-2">
          <div class="label label-key">Last Updated</div>
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
        </div>
      </div>

      <!-- More Information section -->
      <div
        v-if="hasMoreInformation"
        :class="[
          config.gridConfig.source.columnSpan,
          config.gridConfig.source.startColumn,
        ]"
      >
        <div class="label label-key">{{ getLabel("More Information") }}</div>
        <ul class="result-value-small">
          <li v-if="resultData['More Information']">
            {{ getValue("More Information") }}
          </li>
          <li v-else-if="resultData['OUP Book Quote']">
            {{ getValue("OUP Book Quote") }}
          </li>
          <template v-if="hasDomesticValue">
            <template v-if="resultData['Domestic Legal Provisions']">
              <LegalProvisionRenderer
                render-as-li
                :value="getValue('Domestic Legal Provisions')"
                :fallback-data="resultData"
              />
            </template>
            <template v-else-if="resultData['Domestic Instruments ID']">
              <LegalProvisionRenderer
                render-as-li
                skip-article
                :value="getValue('Domestic Instruments ID')"
                :fallback-data="resultData"
              />
            </template>
            <template v-else>
              <li v-if="isLoadingLiterature">
                <LoadingBar class="pt-[11px]" />
              </li>
              <template v-else>
                <template v-if="Array.isArray(domesticValue)">
                  <li v-for="(item, index) in domesticValue" :key="index">
                    <a :href="`/literature/L-${item.id}`">{{ item.title }}</a>
                  </li>
                </template>
                <li v-else>
                  {{ domesticValue }}
                </li>
              </template>
            </template>
          </template>
          <li v-if="relatedCasesCount">
            <a :href="relatedDecisionsLink">
              {{ relatedCasesCount }} related court decisions
            </a>
          </li>
        </ul>
      </div>
    </div>
  </ResultCard>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import ResultCard from "@/components/search-results/ResultCard.vue";
import { answerCardConfig } from "@/config/cardConfigs";
import { literatureCache } from "@/utils/literatureCache";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import LegalProvisionRenderer from "@/components/legal/LegalProvisionRenderer.vue";
import { formatYear } from "@/utils/format";

const props = defineProps({
  resultData: {
    type: Object,
    required: true,
  },
});

const config = answerCardConfig;

// Replace literatureTitles with an array of objects: { id, title }
const literatureTitles = ref([]);

// Updated function to fetch literature titles for a comma‑separated list of IDs,
// returns objects with id and title.
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

// Computed property to display the number of related cases
const relatedCasesCount = computed(() => {
  const links = props.resultData["Court Decisions Link"];
  if (!links) return 0;
  return links.split(",").filter((link) => link.trim() !== "").length;
});

// Updated computed property for the related court decisions link
const relatedDecisionsLink = computed(() => {
  const id = props.resultData["id"];
  return `question/${id}#related-court-decisions`;
});

// New computed property to conditionally show domesticValue bullet
const hasDomesticValue = computed(() => {
  return (
    props.resultData["Domestic Legal Provisions"] ||
    props.resultData["Domestic Instruments ID"] ||
    props.resultData["Literature"]
  );
});

// Update hasMoreInformation to include OUP Book Quote fallback
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

// Last updated value (year only), prefers Last Modified then falls back to Created
const lastUpdatedDisplay = computed(() => {
  const raw = props.resultData["Last Modified"] || props.resultData["Created"];
  const y = formatYear(raw);
  return y ? String(y) : "";
});

// Helper functions to get labels and values with fallbacks
const getLabel = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key);
  return pair?.label || key;
};

const getValue = (key) => {
  const pair = config.keyLabelPairs.find((pair) => pair.key === key);
  const value = props.resultData[key];

  // For key "Answer", split by comma if a string contains commas.
  if (key === "Answer" && typeof value === "string" && value.includes(",")) {
    return value.split(",").map((part) => part.trim());
  }

  if (!value && pair?.emptyValueBehavior) {
    if (pair.emptyValueBehavior.action === "display") {
      return pair.emptyValueBehavior.fallback;
    }
    return "";
  }

  return value;
};

// New helper to compute text classes for a field
const computeTextClasses = (key, baseClass) => {
  const pair = config.keyLabelPairs.find((p) => p.key === key);
  const isEmpty = !props.resultData[key] || props.resultData[key] === "NA";
  const emptyClass =
    isEmpty && pair?.emptyValueBehavior?.action === "display"
      ? "text-gray-300"
      : "";
  return [baseClass, "text-sm leading-relaxed whitespace-pre-line", emptyClass];
};
</script>

<style scoped>
.answer-card-grid {
  display: grid;
  grid-template-columns: repeat(12, var(--column-width));
  column-gap: var(--gutter-width);
  align-items: start;
}

.grid-item {
  display: flex;
  flex-direction: column;
}

.label-key {
  padding: 0;
  margin-top: 12px;
}

.result-value-small li {
  list-style-type: disc; /* Forces bullet points */
  margin-left: 20px; /* Ensures proper indentation */
}
</style>
