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
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import { useEntityData } from "@/composables/useEntityData";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";

const route = useRoute();

const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/arbitral-institution",
  coldId,
);
</script>
