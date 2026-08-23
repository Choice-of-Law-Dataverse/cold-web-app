<template>
  <div>
    <BaseDetailLayout
      table="Regional Instruments"
      :page-heading="data?.title ?? data?.abbreviation ?? ''"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
      entity-type="regional_instrument"
      :entity-id="coldId"
      :entity-title="data?.abbreviation ?? undefined"
    >
      <RegionalInstrumentContent v-if="data" :data="data" />
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.title, data?.abbreviation]"
      fallback="Regional Instrument"
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
import RegionalInstrumentContent from "@/components/entity/content/RegionalInstrumentContent.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useEntityData } from "@/composables/useEntityData";
import { buildLegislationNode } from "@/utils/structuredData";

const route = useRoute();
const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/regional-instrument",
  coldId,
);

const descriptionCandidates = computed(() => [
  data.value?.title,
  data.value?.date ? `Adopted ${data.value.date}` : null,
  "Regional instrument on choice of law in international commercial contracts.",
]);

const breadcrumbs = computed(() => [
  { name: "Home", path: "/" },
  { name: "Regional Instruments", path: "/regional-instrument" },
  {
    name:
      data.value?.title ?? data.value?.abbreviation ?? "Regional Instrument",
    path: `/regional-instrument/${coldId.value}`,
  },
]);

const jsonLd = (siteUrl: string, path: string) =>
  data.value ? buildLegislationNode(siteUrl, path, data.value) : null;
</script>
