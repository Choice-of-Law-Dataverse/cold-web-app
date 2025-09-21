<template>
  <BaseLegalRenderer
    :items="value"
    :value-class-map="valueClassMap"
    :empty-value-behavior="emptyValueBehavior"
    default-class="result-value-small"
  >
    <template #default="{ item }">
      <NuxtLink :to="generateCourtDecisionLink(item)">
        <template v-if="caseTitles[item] !== undefined">
          {{ caseTitles[item] }}
        </template>
        <template v-else>
          <LoadingBar />
        </template>
      </NuxtLink>
    </template>
  </BaseLegalRenderer>
</template>

<script setup>
import { computed } from "vue";
import { useRecordDetailsList } from "@/composables/useRecordDetails";
import BaseLegalRenderer from "./BaseLegalRenderer.vue";
import { NuxtLink } from "#components";
import LoadingBar from "@/components/layout/LoadingBar.vue";

const props = defineProps({
  value: {
    type: [Array, String],
    default: () => [],
  },
  valueClassMap: {
    type: String,
    default: "",
  },
});

// Compute unique IDs and fetch titles via composable
const decisionIds = computed(() => {
  const items = Array.isArray(props.value) ? props.value : [props.value];
  const s = new Set(items.filter(Boolean));
  return Array.from(s);
});

const { data: decisions } = useRecordDetailsList(
  computed(() => "Court Decisions"),
  decisionIds,
);

const caseTitles = computed(() => {
  const map = {};
  decisionIds.value.forEach((id) => {
    const rec = decisions.value?.[id] || {};
    const titleCandidate = rec["Case Title"];
    const finalTitle =
      titleCandidate &&
      titleCandidate !== "NA" &&
      titleCandidate !== "Not found"
        ? titleCandidate
        : rec["Case Citation"] || String(id);
    map[id] = finalTitle;
  });
  return map;
});

// Helper to generate the link URL for a court decision.
function generateCourtDecisionLink(caseId) {
  return `/court-decision/${caseId}`;
}
</script>
