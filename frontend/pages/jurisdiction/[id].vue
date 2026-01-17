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
      <h1 class="mb-4">
        Country Report for {{ jurisdictionData?.Name || "N/A" }}
      </h1>
      <template #search-links>
        <div class="flex flex-col gap-4">
          <DetailRow label="Specialists">
            <div
              v-if="specialistsData && specialistsData.length > 0"
              class="result-value-small"
            >
              <div class="mb-2 flex flex-row flex-wrap gap-2">
                <span
                  v-for="(specialist, i) in specialistsData"
                  :key="i"
                  class="link-chip--static"
                >
                  {{ specialist.Specialist }}
                </span>
              </div>
            </div>
            <div v-else class="prose mb-1">No specialists available</div>
          </DetailRow>
          <DetailRow label="Domestic Instruments" variant="instrument">
            <RelatedDomesticInstruments
              :jurisdiction="jurisdictionData?.Name as string"
              :empty-value-behavior="{
                action: 'display',
                fallback: 'No domestic instruments available',
              }"
            />
          </DetailRow>
          <DetailRow label="Court Decisions" variant="court-decision">
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
              keyLabelPairs.find((pair) => pair.key === 'OUP Chapter')?.label ||
              'OUP Chapter'
            "
            :tooltip="
              jurisdictionConfig.keyLabelPairs.find(
                (pair) => pair.key === 'OUP Chapter',
              )?.tooltip
            "
            variant="oup"
          >
            <RelatedLiterature
              :literature-id="(jurisdictionData?.Literature as string) || ''"
              :mode="'both'"
              :oup-filter="'onlyOup'"
              :jurisdiction="jurisdictionData?.Name as string"
              :use-id="true"
              :value-class-map="valueClassMap['Related Literature']"
              :empty-value-behavior="{
                action: 'display',
                fallback: 'No OUP chapters available',
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
            variant="literature"
          >
            <RelatedLiterature
              :literature-id="(jurisdictionData?.Literature as string) || ''"
              :value-class-map="valueClassMap['Related Literature']"
              :use-id="true"
              :jurisdiction="jurisdictionData?.Name as string"
              :empty-value-behavior="{
                action: 'display',
                fallback: 'No related literature available',
              }"
              :mode="'both'"
              :oup-filter="'noOup'"
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
                  <div class="flex justify-between">
                    <h3 class="comparison-title mb-4">Questionnaire</h3>
                    <span
                      class="mb-4 flex flex-wrap gap-4 text-sm text-cold-purple"
                    >
                      <NuxtLink to="/learn/methodology" class="hover:underline">
                        Methodology
                      </NuxtLink>
                      <NuxtLink to="/learn/glossary" class="hover:underline">
                        Glossary
                      </NuxtLink>
                    </span>
                  </div>
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
import { useSpecialists } from "@/composables/useSpecialists";
import { jurisdictionConfig } from "@/config/pageConfigs";

const route = useRoute();

const { keyLabelPairs, valueClassMap } = jurisdictionConfig;

const { isLoading, data: jurisdictionData } = useJurisdiction(
  computed(() => route.params.id as string),
);

const jurisdictionAlphaCode = computed(
  () => jurisdictionData.value?.alpha3Code as string,
);
const { data: specialistsData } = useSpecialists(jurisdictionAlphaCode);

const keyLabelPairsWithoutLegalFamily = computed(() =>
  keyLabelPairs.filter((pair) => pair.key !== "Legal Family"),
);
</script>
