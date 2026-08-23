<template>
  <div>
    <BaseDetailLayout
      table="Domestic Instruments"
      :page-heading="data?.displayTitle ?? ''"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
      entity-type="domestic_instrument"
      :entity-id="coldId"
      :entity-title="data?.titleInEnglish ?? undefined"
    >
      <DomesticInstrumentContent v-if="data" :data="data" />
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.titleInEnglish, data?.abbreviation]"
      fallback="Domestic Instrument"
      :description-candidates="descriptionCandidates"
      :breadcrumbs="breadcrumbs"
      :json-ld="jsonLd"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DomesticInstrumentContent from "@/components/entity/content/DomesticInstrumentContent.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useEntityData } from "@/composables/useEntityData";
import { buildLegislationNode } from "@/utils/structuredData";

const route = useRoute();

const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/domestic-instrument",
  coldId,
);

const jurisdictionName = computed(
  () => data.value?.relations.jurisdictions[0]?.name ?? null,
);

const descriptionCandidates = computed(() => [
  data.value?.officialTitle,
  jurisdictionName.value
    ? `Choice of law instrument in ${jurisdictionName.value}`
    : null,
  data.value?.entryIntoForce
    ? `In force from ${data.value.entryIntoForce}`
    : null,
  data.value?.relevantProvisions,
]);

const breadcrumbs = computed(() => [
  { name: "Home", path: "/" },
  { name: "Domestic Instruments", path: "/domestic-instrument" },
  {
    name: data.value?.displayTitle ?? "Domestic Instrument",
    path: `/domestic-instrument/${coldId.value}`,
  },
]);

const jsonLd = (siteUrl: string, path: string) =>
  data.value ? buildLegislationNode(siteUrl, path, data.value) : null;
</script>
