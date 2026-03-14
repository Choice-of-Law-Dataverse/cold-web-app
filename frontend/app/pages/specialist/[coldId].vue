<template>
  <div>
    <h1 v-if="data?.specialist" class="sr-only">
      {{ data.specialist }}
    </h1>
    <BaseDetailLayout
      table="Specialists"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
    >
      <SpecialistContent v-if="data" :data="data" />

      <template #footer>
        <LastModified :date="data?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta :title-candidates="[data?.specialist]" fallback="Specialist" />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import SpecialistContent from "@/components/entity/content/SpecialistContent.vue";
import LastModified from "@/components/ui/LastModified.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/specialist", coldId);
</script>
