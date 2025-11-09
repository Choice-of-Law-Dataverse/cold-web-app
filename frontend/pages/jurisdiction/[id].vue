<template>
  <div>
    <BaseDetailLayout
      :loading="isLoading"
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
      <template #search-links>
        <div class="mt-4 flex flex-col gap-4">
          <DetailRow label="Domestic Instruments">
            <RelatedDomesticInstruments
              :jurisdiction="jurisdictionData?.Name as string"
              :empty-value-behavior="{
                action: 'display',
                fallback: 'No domestic instruments available',
              }"
            />
          </DetailRow>
          <DetailRow label="Court Decisions">
            <RelatedCourtDecisions
              :jurisdiction="jurisdictionData?.Name as string"
              :empty-value-behavior="{
                action: 'display',
                fallback: 'No court decisions available',
              }"
            />
          </DetailRow>

          <DetailRow
            :label="
              keyLabelPairs.find((pair) => pair.key === 'Related Literature')
                ?.label || 'Related Literature'
            "
            :tooltip="
              jurisdictionConfig.keyLabelPairs.find(
                (pair) => pair.key === 'Related Literature',
              )?.tooltip
            "
          >
            <RelatedLiterature
              :literature-id="(jurisdictionData?.Literature as string) || ''"
              :value-class-map="valueClassMap['Related Literature']"
              :use-id="true"
              :jurisdiction="jurisdictionData?.Name as string"
              :empty-value-behavior="
                jurisdictionConfig.keyLabelPairs.find(
                  (pair) => pair.key === 'Related Literature',
                )?.emptyValueBehavior
              "
              :mode="'both'"
            />
          </DetailRow>
        </div>
      </template>
    </BaseDetailLayout>
    <ClientOnly>
      <JurisdictionQuestions
        v-if="jurisdictionData"
        :primary-jurisdiction="jurisdictionData"
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
import DetailRow from "@/components/ui/DetailRow.vue";
import JurisdictionQuestions from "@/components/content/JurisdictionQuestions.vue";
import RelatedLiterature from "@/components/literature/RelatedLiterature.vue";
import RelatedCourtDecisions from "@/components/sources/RelatedCourtDecisions.vue";
import RelatedDomesticInstruments from "@/components/sources/RelatedDomesticInstruments.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useJurisdiction } from "@/composables/useJurisdictions";
import { jurisdictionConfig } from "@/config/pageConfigs";

const route = useRoute();

const { keyLabelPairs, valueClassMap } = jurisdictionConfig;

const { isLoading, data: jurisdictionData } =
  useJurisdiction(computed(() => route.params.id as string));

const keyLabelPairsWithoutLegalFamily = computed(() =>
  keyLabelPairs.filter((pair) => pair.key !== "Legal Family"),
);
</script>
