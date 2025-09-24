<template>
  <div>
    <BaseDetailLayout
      :loading="loading"
      :result-data="processedRegionalInstrument || {}"
      :key-label-pairs="computedKeyLabelPairs"
      :value-class-map="valueClassMap"
      :show-suggest-edit="true"
      source-table="Regional Instrument"
    >
      <template #literature>
        <section class="section-gap m-0 p-0">
          <RelatedLiterature
            :literature-id="
              (processedRegionalInstrument?.Literature as string) || ''
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

      <!-- Slot for Legal provisions -->
      <template #regional-legal-provisions="{ value }">
        <!-- Only render if value exists and is not "N/A" -->
        <section
          v-if="value && value.trim() && value.trim() !== 'N/A'"
          class="section-gap m-0 p-0"
        >
          <p class="label mb-[-24px] mt-12 flex flex-row items-center">
            {{
              keyLabelLookup.get("Regional Legal Provisions")?.label ||
              "Selected Provisions"
            }}
            <InfoPopover
              v-if="keyLabelLookup.get('Regional Legal Provisions')?.tooltip"
              :text="keyLabelLookup.get('Regional Legal Provisions')?.tooltip"
            />
          </p>
          <div :class="valueClassMap['Regional Legal Provisions']">
            <div v-if="value && value.trim()">
              <LegalProvision
                v-for="(provisionId, index) in value.split(',')"
                :key="index"
                :provision-id="provisionId"
                :text-type="textType"
                :instrument-title="
                  processedRegionalInstrument
                    ? (processedRegionalInstrument['Abbreviation'] as string) ||
                      (processedRegionalInstrument['Title'] as string)
                    : ''
                "
                table="Regional Legal Provisions"
                @update:has-english-translation="hasEnglishTranslation = $event"
              />
            </div>
          </div>
        </section>
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[
        processedRegionalInstrument?.['Abbreviation'] as string,
      ]"
      fallback="Regional Instrument"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import { useRecordDetails } from "@/composables/useRecordDetails";
import { useDetailDisplay } from "@/composables/useDetailDisplay";
import { regionalInstrumentConfig } from "@/config/pageConfigs";
import RelatedLiterature from "@/components/literature/RelatedLiterature.vue";
import LegalProvision from "@/components/legal/LegalProvision.vue";
import InfoPopover from "@/components/ui/InfoPopover.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import type { TableName } from "@/types/api";

interface RegionalInstrumentRecord {
  Abbreviation?: string;
  "Official Title"?: string;
  [key: string]: unknown;
}

const route = useRoute();
const textType = ref("Full Text of the Provision (English Translation)");
const hasEnglishTranslation = ref(false);

// Use TanStack Vue Query for data fetching - no need for refs with static values
const table = ref<TableName>("Regional Instruments");
const id = ref(route.params.id as string);

const { data: regionalInstrument, isLoading: loading } =
  useRecordDetails<RegionalInstrumentRecord>(table, id);
const { computedKeyLabelPairs, valueClassMap } = useDetailDisplay(
  regionalInstrument,
  regionalInstrumentConfig,
);

// Create lookup map for better performance
const keyLabelLookup = computed(() => {
  const map = new Map();
  computedKeyLabelPairs.value.forEach((pair: { key: string }) => {
    map.set(pair.key, pair);
  });
  // Also include original config pairs for emptyValueBehavior
  regionalInstrumentConfig.keyLabelPairs.forEach((pair) => {
    if (!map.has(pair.key)) {
      map.set(pair.key, pair);
    }
  });
  return map;
});

const processedRegionalInstrument = computed(() => {
  if (!regionalInstrument.value) return null;
  return {
    ...regionalInstrument.value,
    "Title (in English)":
      regionalInstrument.value["Title (in English)"] ||
      regionalInstrument.value["Name"],
    Date: regionalInstrument.value["Date"],
    URL: regionalInstrument.value["URL"] || regionalInstrument.value["Link"],
    Title: (regionalInstrument.value as Record<string, unknown>)["Title"],
    Literature: (regionalInstrument.value as Record<string, unknown>)[
      "Literature"
    ],
  };
});
</script>
