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
        <div>
          <span class="label mb-0.5 flex flex-row items-center">
            {{ keyLabelLookup.get("Publication Title")?.label || "Publication" }}
            <InfoPopover
              v-if="keyLabelLookup.get('Publication Title')?.tooltip"
              :text="keyLabelLookup.get('Publication Title')?.tooltip"
            />
          </span>
          <span class="result-value-small">{{ value }}</span>
        </div>
      </section>
    </template>
    <template #publisher="{ value }">
      <section v-if="value" class="section-gap">
        <div>
          <span class="label mb-0.5 flex flex-row items-center">
            {{ keyLabelLookup.get("Publisher")?.label || "Publisher" }}
            <InfoPopover
              v-if="keyLabelLookup.get('Publisher')?.tooltip"
              :text="keyLabelLookup.get('Publisher')?.tooltip"
            />
          </span>
          <span class="result-value-small">{{ value }}</span>
        </div>
      </section>
    </template>
  </BaseDetailLayout>
  
  <!-- Handle SEO meta tags -->
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
import InfoPopover from "~/components/ui/InfoPopover.vue";
import PageSeoMeta from "~/components/seo/PageSeoMeta.vue";
import { literatureConfig } from "@/config/pageConfigs";
import type { TableName } from "~/types/api";

interface LiteratureRecord {
  Title?: string;
  [key: string]: unknown;
}

const route = useRoute();

// Use TanStack Vue Query for data fetching - no need for refs with static values
const table = ref<TableName>("Literature");
const id = ref(route.params.id as string);

const { data: literature, isLoading: loading } = useRecordDetails<LiteratureRecord>(table, id);

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  literature,
  literatureConfig,
);

// Create lookup map for keyLabelPairs to avoid repetitive find operations
const keyLabelLookup = computed(() => {
  const map = new Map();
  computedKeyLabelPairs.value.forEach(pair => {
    map.set(pair.key, pair);
  });
  return map;
});
</script>
