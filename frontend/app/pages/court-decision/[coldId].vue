<template>
  <div>
    <BaseDetailLayout
      table="Court Decisions"
      :page-heading="data?.displayTitle ?? ''"
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
import CourtDecisionContent from "@/components/entity/content/CourtDecisionContent.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useEntityData } from "@/composables/useEntityData";
import { buildCourtDecisionNode } from "@/utils/structuredData";

const route = useRoute();
const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/court-decision", coldId);

const descriptionCandidates = computed(() => [
  data.value?.caseCitation,
  data.value?.instance,
  data.value?.abstract ?? data.value?.choiceOfLawIssue,
]);

const breadcrumbs = computed(() => [
  { name: "Home", path: "/" },
  { name: "Court Decisions", path: "/court-decision" },
  {
    name: data.value?.displayTitle ?? "Court Decision",
    path: `/court-decision/${coldId.value}`,
  },
]);

const jsonLd = (siteUrl: string, path: string) =>
  data.value ? buildCourtDecisionNode(siteUrl, path, data.value) : null;
</script>
