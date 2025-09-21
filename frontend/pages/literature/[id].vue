<template>
  <BaseDetailLayout
    :loading="loading"
    :result-data="literature"
    :key-label-pairs="computedKeyLabelPairs"
    :value-class-map="valueClassMap"
    :show-suggest-edit="true"
    source-table="Literature"
  >
    <template #publication-title="{ value }">
      <section v-if="value" class="section-gap">
        <div>
          <span class="label mb-0.5 flex flex-row items-center">
            {{
              computedKeyLabelPairs.find(
                (pair) => pair.key === "Publication Title",
              )?.label || "Publication"
            }}
            <InfoPopover
              v-if="
                computedKeyLabelPairs.find(
                  (pair) => pair.key === 'Publication Title',
                )?.tooltip
              "
              :text="
                computedKeyLabelPairs.find(
                  (pair) => pair.key === 'Publication Title',
                )?.tooltip
              "
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
            {{
              computedKeyLabelPairs.find((pair) => pair.key === "Publisher")
                ?.label || "Publisher"
            }}
            <InfoPopover
              v-if="
                computedKeyLabelPairs.find((pair) => pair.key === 'Publisher')
                  ?.tooltip
              "
              :text="
                computedKeyLabelPairs.find((pair) => pair.key === 'Publisher')
                  ?.tooltip
              "
            />
          </span>
          <span class="result-value-small">{{ value }}</span>
        </div>
      </section>
    </template>
  </BaseDetailLayout>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import InfoPopover from "~/components/ui/InfoPopover.vue";
import { literatureConfig } from "@/config/pageConfigs";
import { useHead } from "#imports";

const route = useRoute();

// Use TanStack Vue Query for data fetching
const table = ref("Literature");
const id = ref(route.params.id);

const {
  data: literature,
  isLoading: loading,
  error,
} = useRecordDetails(table, id);

const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  literature,
  literatureConfig,
);

// Set dynamic page title based on 'Title'
watch(
  literature,
  (newVal) => {
    if (!newVal) return;
    const title = newVal["Title"];
    const pageTitle =
      title && title.trim() ? `${title} — CoLD` : "Literature — CoLD";
    useHead({
      title: pageTitle,
      link: [
        {
          rel: "canonical",
          href: `https://cold.global${route.fullPath}`,
        },
      ],
      meta: [
        {
          name: "description",
          content: pageTitle,
        },
      ],
    });
  },
  { immediate: true },
);
</script>
