<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="literature || {}"
      :key-label-pairs="computedKeyLabelPairs"
      :value-class-map="valueClassMap"
      :show-suggest-edit="true"
      source-table="Literature"
    >
      <template #publication-title="{ value }">
        <section v-if="value" class="section-gap">
          <DetailRow
            :label="
              keyLabelLookup.get('Publication Title')?.label || 'Publication'
            "
            :tooltip="keyLabelLookup.get('Publication Title')?.tooltip"
          >
            <span class="result-value-small">{{ value }}</span>
          </DetailRow>
        </section>
      </template>
      <template #publisher="{ value }">
        <section v-if="value" class="section-gap">
          <DetailRow
            :label="keyLabelLookup.get('Publisher')?.label || 'Publisher'"
            :tooltip="keyLabelLookup.get('Publisher')?.tooltip"
          >
            <span class="result-value-small">{{ value }}</span>
          </DetailRow>
        </section>
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[literature?.Title as string]"
      fallback="Literature"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import DetailRow from "@/components/ui/DetailRow.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { literatureConfig } from "@/config/pageConfigs";
import type { TableName } from "@/types/api";

interface LiteratureRecord {
  Title?: string;
  [key: string]: unknown;
}

const route = useRoute();

const table = ref<TableName>("Literature");
const id = ref(route.params.id as string);

const { data: literature, isLoading: loading } =
  useRecordDetails<LiteratureRecord>(table, id);

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  literature,
  literatureConfig,
);

const keyLabelLookup = computed(() => {
  const map = new Map();
  computedKeyLabelPairs.value.forEach((pair) => {
    map.set(pair.key, pair);
  });
  return map;
});
</script>
