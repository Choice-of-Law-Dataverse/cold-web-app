<template>
  <div>
    <h1 v-if="data?.caseTitle" class="sr-only">
      {{ data.caseTitle }}
    </h1>
    <BaseDetailLayout
      table="Court Decisions"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
      entity-type="court_decision"
      :entity-id="coldId"
      :entity-title="data?.caseTitle ?? undefined"
    >
      <CourtDecisionContent v-if="data" :data="data" />
    </BaseDetailLayout>

    <UAlert v-if="error" type="error" class="max-w-container mx-auto mt-4">
      {{ error }}
    </UAlert>

    <PageSeoMeta
      :title-candidates="[
        data?.caseTitle !== 'Not found' ? data?.caseTitle : null,
        data?.caseCitation,
      ]"
      fallback="Court Decision"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import CourtDecisionContent from "@/components/entity/content/CourtDecisionContent.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/court-decision", coldId);
</script>
