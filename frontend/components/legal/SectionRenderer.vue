<template>
  <div>
    <p class="label mb-1 flex flex-row items-center">
      {{ sectionLabel }}
      <InfoPopover v-if="sectionTooltip" :text="sectionTooltip" />
    </p>
    <span v-if="!isLoading">
      <NuxtLink v-if="displayTitle && id" :to="generateInstrumentLink(id)">{{
        displayTitle
      }}</NuxtLink>
      <span v-else>{{ id }}</span>
    </span>
    <LoadingBar v-else />
  </div>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { NuxtLink } from "#components";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  section: {
    type: String,
    default: "Amended by",
  },
  sectionLabel: {
    type: String,
    required: true,
  },
  sectionTooltip: {
    type: String,
    default: "",
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
  // Split at first whitespace
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
  // If loading instrumentTitle, show nothing (handled by LoadingBar)
  if (isLoading.value) return "";
  // Compose display: article part (if any), then instrument title (if any)
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
  // Fallback: if nothing, show id
  return result || props.id;
});

watch(
  () => props.id,
  (newId) => {
    title.value = null;
    // compute the instrument id used for fetching the title
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
  // Handle whitespace after the ID: replace first whitespace after ID with #, remove all further whitespaces
  let idStr = String(instrumentId);
  // Replace the first whitespace after the ID with #
  idStr = idStr.replace(/\s+/, "#");
  // Remove all further whitespaces after the first #
  const hashIndex = idStr.indexOf("#");
  if (hashIndex !== -1) {
    const before = idStr.slice(0, hashIndex + 1);
    const after = idStr.slice(hashIndex + 1).replace(/\s+/g, "");
    idStr = before + after;
  }
  return `/${base}/${idStr}`;
}
</script>
