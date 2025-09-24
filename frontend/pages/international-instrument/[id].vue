<template>
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
          :literature-id="processedInternationalInstrument?.Literature"
          :value-class-map="valueClassMap['Literature']"
          :show-label="true"
          :empty-value-behavior="
            internationalInstrumentConfig.keyLabelPairs.find(
              (pair) => pair.key === 'Literature',
            )?.emptyValueBehavior
          "
          :tooltip="
            computedKeyLabelPairs.find((pair) => pair.key === 'Literature')
              ?.tooltip
          "
          mode="id"
        />
      </section>
    </template>

    <template #selected-provisions>
      <section class="section-gap m-0 p-0">
        <p class="label mb-[-24px] mt-12">
          {{
            computedKeyLabelPairs.find(
              (pair) => pair.key === "Selected Provisions",
            )?.label || "Selected Provisions"
          }}
          <InfoPopover
            v-if="
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Selected Provisions',
              )?.tooltip
            "
            :text="
              computedKeyLabelPairs.find(
                (pair) => pair.key === 'Selected Provisions',
              )?.tooltip
            "
          />
        </p>
        <div :class="valueClassMap['Selected Provisions']">
          <div v-if="provisionsLoading">
            <LoadingBar class="!mt-8" />
          </div>
          <div v-else-if="provisionsError">{{ provisionsError }}</div>
          <div v-else-if="provisions.length">
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
                normalizeAnchorId(provision['Title of the Provision'])
              "
            >
              <template #default>
                {{ provision["Full Text"] }}
              </template>
            </BaseLegalContent>
          </div>
          <div v-else>No provisions found.</div>
        </div>
      </section>
    </template>
  </BaseDetailLayout>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import BaseLegalContent from "@/components/legal/BaseLegalContent.vue";
import InfoPopover from "~/components/ui/InfoPopover.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import { internationalInstrumentConfig } from "@/config/pageConfigs";
import RelatedLiterature from "@/components/literature/RelatedLiterature.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import { useInternationalLegalProvisions } from "@/composables/useInternationalLegalProvisions";
import { useSeoMeta } from "#imports";
import type { TableName } from "~/types/api";

interface InternationalInstrumentRecord {
  Name?: string;  
  [key: string]: unknown;
}

const route = useRoute();

// Use TanStack Vue Query for data fetching - no need for refs with static values
const table = ref<TableName>("International Instruments");
const id = ref(route.params.id as string);

const { data: internationalInstrument, isLoading: loading } = useRecordDetails<InternationalInstrumentRecord>(
  table,
  id,
);
const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  internationalInstrument,
  internationalInstrumentConfig,
);

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
  };
});

// Provisions via composable
const {
  data: provisions,
  isLoading: provisionsLoading,
  error: provisionsError,
} = useInternationalLegalProvisions();

function normalizeAnchorId(str) {
  if (!str) return "";
  // Remove accents/circumflexes, replace whitespace with dash, lowercase
  return str
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/\s+/g, "-")
    .replace(/[^a-zA-Z0-9\-_]/g, "")
    .toLowerCase();
}

// Simplify page title generation with computed property
const pageTitle = computed(() => {
  if (!internationalInstrument.value) return "International Instrument — CoLD";
  const name = internationalInstrument.value["Name"];
  return name?.trim()
    ? `${name} — CoLD`
    : "International Instrument — CoLD";
});

// Use useSeoMeta for better performance
useSeoMeta({
  title: pageTitle,
  description: pageTitle,
  ogTitle: pageTitle,
  ogDescription: pageTitle,
  twitterTitle: pageTitle,
  twitterDescription: pageTitle,
});

// Canonical URL
useHead({
  link: [
    {
      rel: "canonical",
      href: `https://cold.global${route.fullPath}`,
    },
  ],
});
</script>
