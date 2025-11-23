<template>
  <RelatedItemsList
    :items="formattedItems"
    :is-loading="isLoading"
    :base-path="basePath"
    entity-type="instrument"
    :empty-value-behavior="{ action: 'hide' }"
  />
</template>

<script setup>
import { computed } from "vue";
import {
  generateLegalProvisionLink,
  parseLegalProvisionLink,
} from "@/utils/legal";
import { useRecordDetailsList } from "@/composables/useRecordDetails";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";

const props = defineProps({
  value: {
    type: String,
    default: "",
  },
  fallbackData: {
    type: Object,
    required: true,
  },
  valueClassMap: {
    type: Object,
    default: () => ({}),
  },
  skipArticle: {
    type: Boolean,
    default: false,
  },
  renderAsLi: {
    type: Boolean,
    default: false,
  },
});

const provisionItems = computed(() => {
  if (props.value && props.value.trim()) {
    return props.value.split(",");
  }
  if (
    props.fallbackData["Legislation-ID"] &&
    props.fallbackData["Legislation-ID"].trim()
  ) {
    return props.fallbackData["Legislation-ID"].split(",");
  }
  if (
    props.fallbackData["More information"] &&
    props.fallbackData["More information"].trim()
  ) {
    return [props.fallbackData["More information"].replace(/\n/g, " ").trim()];
  }
  return [];
});

const processedProvisions = computed(() =>
  provisionItems.value.map((item) => {
    const { instrumentId, articleId } = parseLegalProvisionLink(item);
    return { raw: item.trim(), instrumentId, articleId };
  }),
);

const instrumentIds = computed(() => {
  const unique = new Set(
    processedProvisions.value.map((p) => p.instrumentId).filter(Boolean),
  );
  return Array.from(unique);
});

const { data: recordMap } = useRecordDetailsList(
  computed(() => "Domestic Instruments"),
  instrumentIds,
);

const instrumentTitles = computed(() => {
  const map = {};
  instrumentIds.value.forEach((id) => {
    const rec = recordMap?.value?.find((r) => r?.id === id) || {};
    const title =
      rec["Abbreviation"] ||
      rec["Title (in English)"] ||
      rec["Title"] ||
      String(id);
    map[id] = title;
  });
  return map;
});

const formatArticle = (article) =>
  article ? article.replace(/(Art\.)(\d+)/, "$1 $2") : "";

const isLoading = computed(() => {
  return processedProvisions.value.some(
    (prov) => !instrumentTitles.value[prov.instrumentId],
  );
});

const basePath = computed(() => "");

const formattedItems = computed(() => {
  return processedProvisions.value
    .map((prov) => {
      const title = instrumentTitles.value[prov.instrumentId];
      if (!title) return null;

      const displayTitle = props.skipArticle
        ? title
        : `${formatArticle(prov.articleId)}, ${title}`;

      return {
        id: generateLegalProvisionLink(prov.raw),
        title: displayTitle,
      };
    })
    .filter(Boolean);
});
</script>
