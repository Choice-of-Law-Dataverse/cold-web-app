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
import { useDomesticInstrumentsList } from "@/composables/useRecordDetails";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import type { RelatedItem } from "@/types/ui";
import type { DomesticInstrument } from "@/types/entities/domestic-instrument";

const props = defineProps<{
  value: string;
  skipArticle?: boolean;
}>();

const processedProvisions = computed(() => {
  if (!props.value?.trim()) return [];
  return props.value.split(",").map((item) => {
    const { instrumentId, articleId } = parseLegalProvisionLink(item);
    return { raw: item.trim(), instrumentId, articleId };
  });
});

const instrumentIds = computed(() => {
  const unique = new Set(
    processedProvisions.value.map((p) => p.instrumentId).filter(Boolean),
  );
  return Array.from(unique);
});

const { data: instruments, isLoading: instrumentsLoading } =
  useDomesticInstrumentsList(instrumentIds);

const instrumentsById = computed(() => {
  const map = new Map<string, DomesticInstrument>();
  if (!instruments.value) return map;
  for (const rec of instruments.value) {
    if (rec) map.set(rec.id, rec);
  }
  return map;
});

const formatArticle = (article: string | undefined) =>
  article ? article.replace(/(Art\.)(\d+)/, "$1 $2") : "";

const isLoading = computed(() => {
  if (instrumentsLoading.value) return true;
  return processedProvisions.value.some(
    (prov) =>
      prov.instrumentId && !instrumentsById.value.has(prov.instrumentId),
  );
});

const formattedItems = computed<RelatedItem[]>(() => {
  const items: RelatedItem[] = [];
  for (const prov of processedProvisions.value) {
    const instrument = instrumentsById.value.get(prov.instrumentId);
    if (!instrument) continue;

    const displayTitle = props.skipArticle
      ? instrument.displayTitle
      : `${formatArticle(prov.articleId)}, ${instrument.displayTitle}`;

    items.push({
      id: generateLegalProvisionLink(prov.raw),
      title: displayTitle,
    });
  }
  return items;
});
</script>
