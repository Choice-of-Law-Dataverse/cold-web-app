<template>
  <div>
    <BaseDetailLayout
      table="Jurisdictions"
      :loading="isLoading"
      :error="error"
      :data="data || {}"
      :labels="jurisdictionLabels"
      :tooltips="jurisdictionTooltips"
      :formatted-jurisdiction="[data?.name as string]"
      :show-suggest-edit="true"
    >
      <DetailRow label="">
        <h1 class="mb-4 text-3xl font-semibold md:text-4xl">
          Country Report for {{ data?.name || "N/A" }}
        </h1>
      </DetailRow>

      <template #search-links>
        <DetailRow label="Specialists">
          <div v-if="specialists.length > 0" class="result-value-small">
            <div class="mb-2 flex flex-row flex-wrap gap-2">
              <span
                v-for="(specialist, i) in specialists"
                :key="i"
                class="link-chip--static"
              >
                {{ specialist.specialist }}
              </span>
            </div>
          </div>
          <div v-else class="prose mb-1">No specialists available</div>
        </DetailRow>
        <DetailRow label="Domestic Instruments" variant="instrument">
          <RelatedItemsList
            :items="domesticInstruments"
            base-path="/domestic-instrument"
          />
        </DetailRow>
        <DetailRow label="Court Decisions" variant="court-decision">
          <RelatedItemsList
            :items="courtDecisions"
            base-path="/court-decision"
          />
        </DetailRow>

        <DetailRow :label="jurisdictionLabels.oupChapter" variant="oup">
          <RelatedItemsList :items="oupLiterature" base-path="/literature" />
        </DetailRow>

        <DetailRow
          :label="jurisdictionLabels.literature"
          :tooltip="jurisdictionTooltips.literature"
          variant="literature"
        >
          <RelatedItemsList :items="nonOupLiterature" base-path="/literature" />
        </DetailRow>
      </template>

      <template #footer>
        <LastModified :date="data?.updatedAt" />
      </template>
    </BaseDetailLayout>
    <ClientOnly>
      <div class="mt-8">
        <JurisdictionComparisonTable
          v-if="jurisdictionOption"
          :primary-jurisdiction="jurisdictionOption"
        />
      </div>
      <template #fallback>
        <div class="mt-8 px-6">
          <div class="max-w-container mx-auto w-full">
            <div class="col-span-12">
              <UCard
                :ui="{
                  body: '!p-0',
                  header: 'border-b-0 px-4 py-5 sm:px-6',
                }"
              >
                <template #header>
                  <div class="flex justify-between">
                    <h3 class="comparison-title mb-4">Comparison</h3>
                    <span class="mb-4 flex flex-wrap gap-2">
                      <UButton
                        to="/learn/methodology"
                        color="primary"
                        variant="ghost"
                        size="xs"
                        leading-icon="i-material-symbols:school-outline"
                        trailing-icon="i-material-symbols:arrow-forward"
                      >
                        Methodology
                      </UButton>
                      <UButton
                        to="/learn/glossary"
                        color="primary"
                        variant="ghost"
                        size="xs"
                        leading-icon="i-material-symbols:dictionary-outline"
                        trailing-icon="i-material-symbols:arrow-forward"
                      >
                        Glossary
                      </UButton>
                    </span>
                  </div>
                </template>
                <div class="gradient-top-border" />
                <div class="px-4 py-5 sm:px-6">
                  <div class="flex flex-col space-y-3 py-8">
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
      :title-candidates="[data?.name as string]"
      fallback="Country Report"
    />

    <EntityFeedback
      entity-type="jurisdiction"
      :entity-id="jurisdictionId"
      :entity-title="data?.name as string"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import JurisdictionComparisonTable from "@/components/jurisdiction/JurisdictionComparisonTable.vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import LastModified from "@/components/ui/LastModified.vue";
import LoadingBar from "@/components/layout/LoadingBar.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { useJurisdictionDetail } from "@/composables/useRecordDetails";
import { jurisdictionLabels } from "@/config/labels";
import { jurisdictionTooltips } from "@/config/tooltips";
import type { RelatedItem } from "@/types/ui";

const route = useRoute();
const jurisdictionId = ref(route.params.id as string);

const { isLoading, data, error } = useJurisdictionDetail(jurisdictionId);

const specialists = computed(() => data.value?.relations.specialists ?? []);

const courtDecisions = computed<RelatedItem[]>(() =>
  (data.value?.relations.courtDecisions ?? []).map((cd) => ({
    id: cd.coldId || String(cd.id),
    title: cd.caseTitle || cd.caseCitation || String(cd.id),
  })),
);

const domesticInstruments = computed<RelatedItem[]>(() =>
  (data.value?.relations.domesticInstruments ?? []).map((di) => ({
    id: di.coldId || String(di.id),
    title:
      di.titleInEnglish || di.officialTitle || di.abbreviation || String(di.id),
  })),
);

const oupLiterature = computed<RelatedItem[]>(() =>
  (data.value?.relations.literature ?? [])
    .filter((lit) => Boolean(lit.oupJdChapter))
    .map((lit) => ({
      id: lit.coldId || String(lit.id),
      title: lit.title || String(lit.id),
    })),
);

const nonOupLiterature = computed<RelatedItem[]>(() =>
  (data.value?.relations.literature ?? [])
    .filter((lit) => !lit.oupJdChapter)
    .map((lit) => ({
      id: lit.coldId || String(lit.id),
      title: lit.title || String(lit.id),
    })),
);

const jurisdictionOption = computed(() => {
  if (!data.value) return null;
  return {
    name: data.value.name || "",
    label: data.value.name || "",
    alpha3Code: data.value.alpha3Code || "",
  };
});
</script>
