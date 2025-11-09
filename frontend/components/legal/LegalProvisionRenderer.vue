<template>
  <template v-for="(prov, index) in processedProvisions" :key="index">
    <template v-if="renderAsLi">
      <li>
        <NuxtLink
          class="text-cold-purple"
          :to="generateLegalProvisionLink(prov.raw)"
        >
          <template v-if="instrumentTitles[prov.instrumentId]">
            <template v-if="!skipArticle">
              {{ formatArticle(prov.articleId) }},
              {{ instrumentTitles[prov.instrumentId] }}
            </template>
            <template v-else>
              {{ instrumentTitles[prov.instrumentId] }}
            </template>
          </template>
          <template v-else>
            <LoadingBar class="pt-[9px]" />
          </template>
        </NuxtLink>
      </li>
    </template>
    <template v-else>
      <NuxtLink
        class="text-cold-purple"
        :to="generateLegalProvisionLink(prov.raw)"
      >
        <template v-if="instrumentTitles[prov.instrumentId]">
          <template v-if="!skipArticle">
            {{ formatArticle(prov.articleId) }},
            {{ instrumentTitles[prov.instrumentId] }}
          </template>
          <template v-else>
            {{ instrumentTitles[prov.instrumentId] }}
          </template>
        </template>
        <template v-else>
          <LoadingBar class="pt-[9px]" />
        </template>
      </NuxtLink>
    </template>
  </template>
</template>

<script setup>
import { computed, watch } from "vue";
import {
  generateLegalProvisionLink,
  parseLegalProvisionLink,
} from "@/utils/legal";
import { useRecordDetailsList } from "@/composables/useRecordDetails";
import LoadingBar from "@/components/layout/LoadingBar.vue";

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
watch(
  processedProvisions,
  () => {
    /* IDs are computed reactively; useRecordDetailsList handles fetching */
  },
  { immediate: true },
);
</script>

<style scoped>
li {
  list-style-type: disc;
  margin-left: 20px;
}
</style>
