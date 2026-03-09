<template>
  <div>
    <h1 v-if="data?.title" class="sr-only">
      {{ data.title }}
    </h1>
    <BaseDetailLayout
      table="Literature"
      :loading="isLoading"
      :error="error"
      :data="data || {}"
      :show-suggest-edit="true"
    >
      <LiteratureContent v-if="data" :data="data" />

      <template #footer>
        <LastModified :date="data?.updatedAt as string" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[data?.title as string]"
      fallback="Literature"
    />

    <EntityFeedback
      entity-type="literature"
      :entity-id="id"
      :entity-title="data?.title as string"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import LiteratureContent from "@/components/entity/content/LiteratureContent.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();

const id = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/literature", id);
</script>
