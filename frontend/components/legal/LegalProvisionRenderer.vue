<template>
  <RelatedItemsList
    :items="formattedItems"
    :is-loading="isLoading"
    :base-path="''"
    :empty-value-behavior="{ action: 'hide' }"
  />
</template>

<script setup lang="ts">
import { computed } from "vue";
import {
  generateLegalProvisionLink,
  parseLegalProvisionLink,
} from "@/utils/legal";
import { useRecordDetailsList } from "@/composables/useRecordDetails";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import type { RelatedItem } from "@/types/ui";
import type { DomesticInstrumentResponse } from "@/types/entities/domestic-instrument";

const props = defineProps<{
  value: string;
  skipArticle?: boolean;
}>();

const provisionItems = computed(() => {
  if (props.value && props.value.trim()) {
    return props.value.split(",");
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

const { data: recordMap } = useRecordDetailsList<DomesticInstrumentResponse>(
  computed(() => "Domestic Instruments"),
  instrumentIds,
);

const instrumentTitles = computed(() => {
  const map: Record<string, string> = {};
  instrumentIds.value.forEach((id) => {
    const rec = recordMap?.value?.find((r) => r?.id === id);
    const title =
      rec?.Abbreviation ||
      rec?.["Title (in English)"] ||
      rec?.["Official Title"] ||
      String(id);
    map[id] = title;
  });
  return map;
});

const formatArticle = (article: string | undefined) =>
  article ? article.replace(/(Art\.)(\d+)/, "$1 $2") : "";

const isLoading = computed(() => {
  return processedProvisions.value.some(
    (prov) => !instrumentTitles.value[prov.instrumentId],
  );
});

const formattedItems = computed<RelatedItem[]>(() => {
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
    .filter((item): item is RelatedItem => item !== null);
});
</script>
