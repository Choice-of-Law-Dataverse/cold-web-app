<template>
  <div>
    <h1 v-if="data?.title" class="sr-only">
      {{ data.title }}
    </h1>
    <BaseDetailLayout
      table="Literature"
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

    <PageSeoMeta :title-candidates="[data?.title]" fallback="Literature" />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import LiteratureContent from "@/components/entity/content/LiteratureContent.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();

const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/literature", coldId);
</script>
