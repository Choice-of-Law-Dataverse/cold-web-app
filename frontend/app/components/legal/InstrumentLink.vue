<template>
  <span v-if="!isLoading">
    <NuxtLink
      v-if="displayTitle && id"
      class="text-cold-purple"
      :to="generateInstrumentLink(id)"
      >{{ displayTitle }}</NuxtLink
    >
    <span v-else>{{ id }}</span>
  </span>
  <LoadingBar v-else />
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { NuxtLink } from "#components";
import LoadingBar from "@/components/layout/LoadingBar.vue";

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  table: {
    type: String,
    default: "Domestic Instruments",
  },
});

const title = ref(null);
const instrumentTitleId = ref("");
const articlePart = ref("");

function parseIdParts(id) {
  const match = String(id).match(/^(\S+)\s+(.+)$/);
  if (match) {
    return { instrumentId: match[1], article: match[2] };
  } else {
    return { instrumentId: id, article: "" };
  }
}

const { data: record, isLoading } = useRecordDetails(
  computed(() => props.table),
  instrumentTitleId,
);

const displayTitle = computed(() => {
  if (isLoading.value) return "";
  let result = "";
  if (articlePart.value) {
    result += articlePart.value;
  }
  const rec = record.value || {};
  let derivedTitle =
    rec["Abbreviation"] || rec["Title (in English)"] || rec["Title"] || "";
  if (!derivedTitle) {
    const ct = rec["Case Title"];
    derivedTitle =
      ct && ct !== "NA" && ct !== "Not found" ? ct : rec["Case Citation"] || "";
  }
  if (derivedTitle) {
    if (result) result += ", ";
    result += derivedTitle;
  }
  return result || props.id;
});

watch(
  () => props.id,
  (newId) => {
    title.value = null;
    articlePart.value = "";
    const { instrumentId, article } = parseIdParts(newId);
    articlePart.value = article;
    instrumentTitleId.value = String(instrumentId);
  },
  { immediate: true },
);

function generateInstrumentLink(instrumentId) {
  let base = props.table.toLowerCase().replace(/\s+/g, "-");
  if (base.endsWith("s")) {
    base = base.slice(0, -1);
  }
  let idStr = String(instrumentId);
  idStr = idStr.replace(/\s+/, "#");
  const hashIndex = idStr.indexOf("#");
  if (hashIndex !== -1) {
    const before = idStr.slice(0, hashIndex + 1);
    const after = idStr.slice(hashIndex + 1).replace(/\s+/g, "");
    idStr = before + after;
  }
  return `/${base}/${idStr}`;
}
</script>
