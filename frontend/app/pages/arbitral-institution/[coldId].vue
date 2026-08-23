<template>
  <div>
    <BaseDetailLayout
      table="Arbitral Institutions"
      :page-heading="data?.institution ?? ''"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
    >
      <EntityContent
        v-if="data"
        base-path="/arbitral-institution"
        :data="data"
      />
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.institution, data?.abbreviation]"
      fallback="Arbitral Institution"
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
import EntityContent from "@/components/entity/EntityContent.vue";
import { useEntityData } from "@/composables/useEntityData";
import { buildArbitralInstitutionNode } from "@/utils/structuredData";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";

const route = useRoute();

const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/arbitral-institution",
  coldId,
);

const descriptionCandidates = computed(() => [
  data.value?.institution,
  data.value?.abbreviation,
  "Arbitral institution recorded in the Choice of Law Dataverse, with its arbitral rules and awards.",
]);

const breadcrumbs = computed(() => [
  { name: "Home", path: "/" },
  { name: "Arbitral Institutions", path: "/arbitral-institution" },
  {
    name: data.value?.institution ?? "Arbitral Institution",
    path: `/arbitral-institution/${coldId.value}`,
  },
]);

const jsonLd = (siteUrl: string, path: string) =>
  data.value ? buildArbitralInstitutionNode(siteUrl, path, data.value) : null;
</script>
