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

    <PageSeoMeta :title-candidates="[data?.specialist]" fallback="Specialist" />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import SpecialistContent from "@/components/entity/content/SpecialistContent.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/specialist", coldId);
</script>
