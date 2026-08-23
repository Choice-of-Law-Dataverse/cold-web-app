<template>
  <div>
    <BaseDetailLayout
      table="Literature"
      :page-heading="data?.displayTitle ?? ''"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
      entity-type="literature"
      :entity-id="coldId"
      :entity-title="data?.title ?? undefined"
    >
      <LiteratureContent v-if="data" :data="data" />
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.title, data?.author]"
      fallback="Literature"
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
import LiteratureContent from "@/components/entity/content/LiteratureContent.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useEntityData } from "@/composables/useEntityData";
import { buildLiteratureNode } from "@/utils/structuredData";

const route = useRoute();

const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/literature", coldId);

const descriptionCandidates = computed(() => [
  data.value?.author,
  data.value?.publicationTitle,
  data.value?.publicationYear ? String(data.value.publicationYear) : null,
  data.value?.abstractNote,
]);

const breadcrumbs = computed(() => [
  { name: "Home", path: "/" },
  { name: "Literature", path: "/literature" },
  {
    name: data.value?.displayTitle ?? "Literature",
    path: `/literature/${coldId.value}`,
  },
]);

const jsonLd = (siteUrl: string, path: string) =>
  data.value ? buildLiteratureNode(siteUrl, path, data.value) : null;
</script>
