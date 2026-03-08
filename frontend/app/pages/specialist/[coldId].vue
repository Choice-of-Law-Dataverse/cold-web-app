<template>
  <div>
    <h1 v-if="specialist?.specialist" class="sr-only">
      {{ specialist.specialist }}
    </h1>
    <BaseDetailLayout
      table="Specialists"
      :loading="loading"
      :error="error"
      :data="specialist || {}"
      :field-order="entityConfig.fieldOrder"
      :label-overrides="entityConfig.labelOverrides"
      :tooltips="entityConfig.tooltips"
      :relations="specialist?.relations"
      :show-suggest-edit="true"
    >
      <template #website="{ value, label }">
        <DetailRow :label="label">
          <a
            :href="String(value)"
            target="_blank"
            rel="noopener noreferrer"
            class="text-primary break-all hover:underline"
          >
            {{ value }}
          </a>
        </DetailRow>
      </template>

      <template #footer>
        <LastModified :date="specialist?.updatedAt" />
      </template>
    </BaseDetailLayout>

    <PageSeoMeta
      :title-candidates="[specialist?.specialist]"
      fallback="Specialist"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import LastModified from "@/components/ui/LastModified.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useSpecialistDetail } from "@/composables/useRecordDetails";
import { getEntityConfig } from "@/config/entityRegistry";

const entityConfig = getEntityConfig("/specialist")!;

const route = useRoute();
const specialistId = ref(route.params.coldId as string);

const {
  data: specialist,
  isLoading: loading,
  error,
} = useSpecialistDetail(specialistId);
</script>
