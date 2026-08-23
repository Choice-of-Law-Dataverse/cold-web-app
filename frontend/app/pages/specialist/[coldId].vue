<template>
  <div>
    <BaseDetailLayout
      table="Specialists"
      :page-heading="data?.specialist ?? ''"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
    >
      <SpecialistContent v-if="data" :data="data" />
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.specialist, data?.affiliation]"
      fallback="Specialist"
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
import SpecialistContent from "@/components/entity/content/SpecialistContent.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useEntityData } from "@/composables/useEntityData";
import { buildSpecialistNode } from "@/utils/structuredData";

const route = useRoute();
const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/specialist", coldId);

const descriptionCandidates = computed(() => [
  data.value?.affiliation,
  data.value?.bio,
  data.value?.specialist
    ? `${data.value.specialist} is listed as a choice of law specialist in the Choice of Law Dataverse.`
    : null,
]);

const breadcrumbs = computed(() => [
  { name: "Home", path: "/" },
  { name: "Specialists", path: "/specialist" },
  {
    name: data.value?.specialist ?? "Specialist",
    path: `/specialist/${coldId.value}`,
  },
]);

const jsonLd = (siteUrl: string, path: string) =>
  data.value ? buildSpecialistNode(siteUrl, path, data.value) : null;
</script>
