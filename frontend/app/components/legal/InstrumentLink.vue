<template>
  <span v-if="isLoading">
    <LoadingBar />
  </span>
  <InlineError v-else-if="error" :error="error" />
  <span v-else>
    <NuxtLink
      v-if="displayTitle && id"
      class="text-cold-purple"
      :to="generateInstrumentLink(id)"
      >{{ displayTitle }}</NuxtLink
    >
    <span v-else>{{ id }}</span>
  </span>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { NuxtLink } from "#components";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import InlineError from "@/components/ui/InlineError.vue";
import type { TableName } from "@/types/api";

const props = withDefaults(
  defineProps<{
    id: string;
    table?: TableName;
  }>(),
  { table: "Domestic Instruments" },
);

const title = ref<string | null>(null);
const instrumentTitleId = ref("");
const articlePart = ref("");

function parseIdParts(id: string) {
  const match = String(id).match(/^(\S+)\s+(.+)$/);
  if (match) {
    return { instrumentId: match[1] ?? id, article: match[2] ?? "" };
  }
  return { instrumentId: id, article: "" };
}

const {
  data: record,
  isLoading,
  error,
} = useRecordDetails(props.table, instrumentTitleId);

const displayTitle = computed(() => {
  if (isLoading.value) return "";
  let result = "";
  if (articlePart.value) {
    result += articlePart.value;
  }
  const rec = (record.value || {}) as Record<string, string | undefined>;
  let derivedTitle = rec.abbreviation || rec.titleInEnglish || rec.title || "";
  if (!derivedTitle) {
    const ct = rec.caseTitle;
    derivedTitle =
      ct && ct !== "NA" && ct !== "Not found" ? ct : rec.caseCitation || "";
  }
  if (derivedTitle) {
    if (result) result += ", ";
    result += derivedTitle;
  }
  return result || props.id;
});

watch(
  () => props.id,
  (newId: string) => {
    title.value = null;
    articlePart.value = "";
    const { instrumentId, article } = parseIdParts(newId);
    articlePart.value = article;
    instrumentTitleId.value = String(instrumentId);
  },
  { immediate: true },
);

function generateInstrumentLink(instrumentId: string) {
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
