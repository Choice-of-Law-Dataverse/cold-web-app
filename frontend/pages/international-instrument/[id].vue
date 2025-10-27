<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="processedInternationalInstrument || {}"
      :key-label-pairs="computedKeyLabelPairs"
      :value-class-map="valueClassMap"
      :show-suggest-edit="true"
      source-table="International Instrument"
    >
      <template #literature>
        <section class="section-gap m-0 p-0">
          <RelatedLiterature
            :literature-id="
              (processedInternationalInstrument?.Literature as string) || ''
            "
            :value-class-map="valueClassMap['Literature']"
            :show-label="true"
            :empty-value-behavior="
              keyLabelLookup.get('Literature')?.emptyValueBehavior
            "
            :tooltip="keyLabelLookup.get('Literature')?.tooltip"
            mode="id"
          />
        </section>
      </template>

      <template #selected-provisions>
        <div class="flex flex-col md:w-full md:flex-row md:gap-6">
          <h4 class="label label-key mt-0 md:w-48 md:flex-shrink-0">
            <span class="flex items-center">
              {{
                keyLabelLookup.get("Selected Provisions")?.label ||
                "Selected Provisions"
              }}
              <InfoPopover
                v-if="keyLabelLookup.get('Selected Provisions')?.tooltip"
                :text="keyLabelLookup.get('Selected Provisions')?.tooltip"
              />
            </span>
          </h4>
          <div class="provisions-container md:flex-1">
            <div v-if="provisionsLoading">
              <LoadingBar class="!mt-8" />
            </div>
            <div v-else-if="provisionsError">{{ provisionsError }}</div>
            <div v-else-if="provisions && provisions.length">
              <BaseLegalContent
                v-for="(provision, index) in provisions"
                :key="index"
                :title="
                  provision['Title of the Provision'] +
                  (processedInternationalInstrument
                    ? ', ' +
                      (processedInternationalInstrument['Abbreviation'] ||
                        processedInternationalInstrument['Title (in English)'])
                    : '')
                "
                :anchor-id="
                  normalizeAnchorId(
                    String(provision['Title of the Provision'] || ''),
                  )
                "
              >
                <template #default>
                  {{ provision["Full Text"] }}
                </template>
              </BaseLegalContent>
            </div>
            <div v-else>No provisions found.</div>
          </div>
        </div>
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[internationalInstrument?.['Name'] as string]"
      fallback="International Instrument"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import BaseLegalContent from "@/components/legal/BaseLegalContent.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import { internationalInstrumentConfig } from "@/config/pageConfigs";
import RelatedLiterature from "@/components/literature/RelatedLiterature.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import { useInternationalLegalProvisions } from "@/composables/useInternationalLegalProvisions";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import type { TableName } from "@/types/api";

interface InternationalInstrumentRecord {
  Name?: string;
  [key: string]: unknown;
}

const route = useRoute();

// Use TanStack Vue Query for data fetching - no need for refs with static values
const table = ref<TableName>("International Instruments");
const id = ref(route.params.id as string);

const { data: internationalInstrument, isLoading: loading } =
  useRecordDetails<InternationalInstrumentRecord>(table, id);
const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  internationalInstrument,
  internationalInstrumentConfig,
);

// Create lookup map for better performance
const keyLabelLookup = computed(() => {
  const map = new Map();
  computedKeyLabelPairs.value.forEach((pair: { key: string }) => {
    map.set(pair.key, pair);
  });
  // Also include original config pairs for emptyValueBehavior
  internationalInstrumentConfig.keyLabelPairs.forEach((pair) => {
    if (!map.has(pair.key)) {
      map.set(pair.key, pair);
    }
  });
  return map;
});

const processedInternationalInstrument = computed(() => {
  if (!internationalInstrument.value) return null;
  return {
    ...internationalInstrument.value,
    "Title (in English)":
      internationalInstrument.value["Title (in English)"] ||
      internationalInstrument.value["Name"],
    Date: internationalInstrument.value["Date"],
    URL:
      internationalInstrument.value["URL"] ||
      internationalInstrument.value["Link"],
    Literature: (internationalInstrument.value as Record<string, unknown>)[
      "Literature"
    ],
    Abbreviation: (internationalInstrument.value as Record<string, unknown>)[
      "Abbreviation"
    ],
  };
});

// Provisions via composable
const {
  data: provisions,
  isLoading: provisionsLoading,
  error: provisionsError,
} = useInternationalLegalProvisions();

function normalizeAnchorId(str: string): string {
  if (!str) return "";
  // Remove accents/circumflexes, replace whitespace with dash, lowercase
  return str
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/\s+/g, "-")
    .replace(/[^a-zA-Z0-9\-_]/g, "")
    .toLowerCase();
}
</script>

<style scoped>
/* Remove the extra spacer from BaseLegalContent when provisions are in a two-column layout */
.provisions-container :deep(.base-legal-content .no-margin > div:first-child) {
  display: none;
}
</style>
