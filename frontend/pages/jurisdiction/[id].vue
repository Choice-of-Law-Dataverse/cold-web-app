<template>
  <div>
    <BaseDetailLayout
      table="Jurisdictions"
      :loading="isLoading"
      :data="jurisdictionData || {}"
      :labels="jurisdictionLabels"
      :tooltips="jurisdictionTooltips"
      :formatted-jurisdiction="[jurisdictionData?.Name as {}]"
      :show-suggest-edit="true"
    >
      <DetailRow label="">
        <h1 class="mb-4 text-3xl font-semibold md:text-4xl">
          Country Report for {{ jurisdictionData?.Name || "N/A" }}
        </h1>
      </DetailRow>

      <template #search-links>
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
          />
        </DetailRow>
        <DetailRow label="Court Decisions" variant="court-decision">
          <RelatedCourtDecisions
            :jurisdiction="jurisdictionData?.Name as string"
          />
        </DetailRow>

        <DetailRow :label="jurisdictionLabels['OUP Chapter']" variant="oup">
          <RelatedLiterature
            :literature-id="(jurisdictionData?.Literature as string) || ''"
            :mode="'both'"
            :oup-filter="'onlyOup'"
            :jurisdiction="jurisdictionData?.Name as string"
          />
        </DetailRow>

        <DetailRow
          :label="jurisdictionLabels['Literature']"
          :tooltip="jurisdictionTooltips['Literature']"
          variant="literature"
        >
          <RelatedLiterature
            :literature-id="(jurisdictionData?.Literature as string) || ''"
            :jurisdiction="jurisdictionData?.Name as string"
            :mode="'both'"
            :oup-filter="'noOup'"
          />
        </DetailRow>
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
                    <h3
                      class="comparison-title mb-4 text-xl font-semibold md:text-2xl"
                    >
                      Questionnaire
                    </h3>
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
import { jurisdictionLabels } from "@/config/labels";
import { jurisdictionTooltips } from "@/config/tooltips";

const route = useRoute();

const { isLoading, data: jurisdictionData } = useJurisdiction(
  computed(() => route.params.id as string),
);

const jurisdictionAlphaCode = computed(
  () => jurisdictionData.value?.alpha3Code as string,
);
const { data: specialistsData } = useSpecialists(jurisdictionAlphaCode);
</script>
