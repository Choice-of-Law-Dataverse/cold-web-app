<template>
  <div>
    <BaseDetailLayout
      :loading="isLoading.value"
      :result-data="jurisdictionData || {}"
      :key-label-pairs="keyLabelPairsWithoutLegalFamily"
      :value-class-map="valueClassMap"
      :formatted-jurisdiction="[jurisdictionData?.Name as {}]"
      :show-suggest-edit="true"
      source-table="Jurisdiction"
    >
      <h1 class="mb-12">
        Country Report for {{ jurisdictionData?.Name || "N/A" }}
      </h1>
      <template #related-literature>
        <section class="section-gap m-0 p-0">
          <div class="flex flex-col md:w-full md:flex-row md:items-start md:gap-6">
            <div class="label label-key mt-0 md:w-48 md:flex-shrink-0">
              <span class="flex items-center">
                {{
                  keyLabelPairs.find((pair) => pair.key === 'Related Literature')
                    ?.label || 'Related Literature'
                }}
                <InfoPopover
                  v-if="
                    jurisdictionConfig.keyLabelPairs.find(
                      (pair) => pair.key === 'Related Literature',
                    )?.tooltip
                  "
                  :text="
                    jurisdictionConfig.keyLabelPairs.find(
                      (pair) => pair.key === 'Related Literature',
                    )?.tooltip
                  "
                />
              </span>
            </div>
            <div class="md:flex-1">
              <RelatedLiterature
                :literature-id="(jurisdictionData?.Literature as string) || ''"
                :value-class-map="valueClassMap['Related Literature']"
                :use-id="true"
                :show-label="false"
                :empty-value-behavior="
                  jurisdictionConfig.keyLabelPairs.find(
                    (pair) => pair.key === 'Related Literature',
                  )?.emptyValueBehavior
                "
                mode="id"
              />
            </div>
          </div>
        </section>
      </template>

      <template #search-links>
        <template
          v-if="
            courtDecisionCountLoading ||
            domesticInstrumentCountLoading ||
            (courtDecisionCount !== 0 && courtDecisionCount !== null) ||
            (domesticInstrumentCount !== 0 && domesticInstrumentCount !== null)
          "
        >
          <template
            v-if="courtDecisionCountLoading || domesticInstrumentCountLoading"
          >
            <LoadingBar />
          </template>
          <template v-else>
            <div
              class="flex flex-col md:w-full md:flex-row md:items-start md:gap-6"
            >
              <h4 class="label label-key mt-0 md:w-48 md:flex-shrink-0">
                <span class="flex items-center"> Related Data </span>
              </h4>

              <div class="flex flex-col gap-2 md:flex-1">
                <NuxtLink
                  v-if="courtDecisionCount !== 0 && courtDecisionCount !== null"
                  :to="{
                    name: 'search',
                    query: {
                      type: 'Court Decisions',
                      jurisdiction: (jurisdictionData?.Name as string) || '',
                    },
                  }"
                  class="!mb-2 no-underline"
                >
                  <UButton class="link-button" variant="link">
                    <span class="break-words text-left">
                      <template v-if="courtDecisionCount !== null">
                        See {{ courtDecisionCount }} court decision{{
                          courtDecisionCount === 1 ? "" : "s"
                        }}
                        from {{ jurisdictionData?.Name || "N/A" }}
                      </template>
                      <template v-else>
                        All court decisions from
                        {{ jurisdictionData?.Name || "N/A" }}
                      </template>
                    </span>
                  </UButton>
                </NuxtLink>

                <NuxtLink
                  v-if="
                    domesticInstrumentCount !== 0 &&
                    domesticInstrumentCount !== null
                  "
                  :to="{
                    name: 'search',
                    query: {
                      type: 'Domestic Instruments',
                      jurisdiction: (jurisdictionData?.Name as string) || '',
                    },
                  }"
                  class="no-underline"
                >
                  <UButton class="link-button" variant="link">
                    <span class="break-words text-left">
                      <template v-if="domesticInstrumentCount !== null">
                        See {{ domesticInstrumentCount }} domestic instrument{{
                          domesticInstrumentCount === 1 ? "" : "s"
                        }}
                        from {{ jurisdictionData?.Name || "N/A" }}
                      </template>
                      <template v-else>
                        All domestic instruments from
                        {{ jurisdictionData?.Name || "N/A" }}
                      </template>
                    </span>
                  </UButton>
                </NuxtLink>
              </div>
            </div>
          </template>
        </template>
      </template>
    </BaseDetailLayout>
    <JurisdictionSelector
      v-if="jurisdictionData"
      :formatted-jurisdiction="jurisdictionData"
    />
    <ClientOnly>
      <JurisdictionQuestions
        v-if="jurisdictionData?.Name"
        :formatted-jurisdiction="[jurisdictionData.Name]"
      />
      <template #fallback>
        <div class="px-6">
          <div class="mx-auto w-full max-w-container">
            <div class="col-span-12">
              <UCard class="cold-ucard">
                <div>
                  <h2 class="mb-8 mt-2">
                    Questions and Answers
                    {{
                      jurisdictionData?.Name
                        ? `for ${jurisdictionData.Name}`
                        : ""
                    }}
                  </h2>
                  <div class="ml-8 flex flex-col space-y-3 py-8">
                    <LoadingBar />
                    <LoadingBar />
                    <LoadingBar />
                  </div>
                </div>
              </UCard>
            </div>
          </div>
        </div>
      </template>
    </ClientOnly>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[jurisdictionData?.Name as string]"
      fallback="Country Report"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
// import JurisdictionComparison from '@/components/jurisdiction-comparison/JurisdictionComparison.vue'
import JurisdictionSelector from "@/components/ui/JurisdictionSelector.vue";
import JurisdictionQuestions from "@/components/content/JurisdictionQuestions.vue";
import RelatedLiterature from "@/components/literature/RelatedLiterature.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useJurisdiction } from "@/composables/useJurisdictions";
import {
  useDomesticInstrumentsCount,
  useCourtDecisionsCount,
} from "@/composables/useJurisdictionCounts";
import { jurisdictionConfig } from "@/config/pageConfigs";

const route = useRoute();

const { keyLabelPairs, valueClassMap } = jurisdictionConfig;

const compareJurisdiction = ref<string | null>(null);

const { isLoading: isJurisdictionLoading, data: jurisdictionData } =
  useJurisdiction(computed(() => route.params.id as string));

const { data: courtDecisionCount, isLoading: courtDecisionCountLoading } =
  useCourtDecisionsCount(
    computed(() => jurisdictionData.value?.Name as string),
  );

const {
  data: domesticInstrumentCount,
  isLoading: domesticInstrumentCountLoading,
} = useDomesticInstrumentsCount(
  computed(() => jurisdictionData.value?.Name as string),
);

// Remove Legal Family from keyLabelPairs for detail display
const keyLabelPairsWithoutLegalFamily = computed(() =>
  keyLabelPairs.filter((pair) => pair.key !== "Legal Family"),
);

// Set compare jurisdiction from query parameter
compareJurisdiction.value = (route.query.c as string) || null;

const isLoading = computed(
  () =>
    isJurisdictionLoading ||
    // literatureLoading ||
    // specialistsLoading ||
    courtDecisionCountLoading ||
    domesticInstrumentCountLoading,
);
</script>
