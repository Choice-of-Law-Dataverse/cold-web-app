<template>
  <div>
    <h1 v-if="data?.caseTitle" class="sr-only">
      {{ data.caseTitle }}
    </h1>
    <BaseDetailLayout
      table="Court Decisions"
      :loading="isLoading"
      :error="error"
      :data="data || {}"
      :show-suggest-edit="true"
    >
      <CourtDecisionContent v-if="data" :data="data" />

      <template #footer>
        <JurisdictionReportBanner
          :jurisdiction-code="
            (primaryJurisdiction?.coldId as string) ?? undefined
          "
          :jurisdiction-name="
            (primaryJurisdiction?.name as string) ?? undefined
          "
        />
        <LastModified :date="data?.updatedAt as string" />
      </template>
    </BaseDetailLayout>

    <UAlert v-if="error" type="error" class="max-w-container mx-auto mt-4">
      {{ error }}
    </UAlert>

    <PageSeoMeta
      :title-candidates="[
        (data?.caseTitle as string) !== 'Not found'
          ? (data?.caseTitle as string)
          : null,
        data?.caseCitation as string,
      ]"
      fallback="Court Decision"
    />

    <EntityFeedback
      entity-type="court_decision"
      :entity-id="courtDecisionId"
      :entity-title="data?.caseTitle as string"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import CourtDecisionContent from "@/components/entity/content/CourtDecisionContent.vue";
import JurisdictionReportBanner from "@/components/jurisdiction/JurisdictionReportBanner.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import LastModified from "@/components/ui/LastModified.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const courtDecisionId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData(
  "/court-decision",
  courtDecisionId,
);

const primaryJurisdiction = computed(() => {
  const rels = data.value?.relations as
    | Record<string, Record<string, unknown>[]>
    | undefined;
  return rels?.jurisdictions?.[0] ?? null;
});
</script>
