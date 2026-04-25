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
    >
      <template #title-actions>
        <template v-if="data">
          <PdfLink
            :pdf-field="data.officialSourcePdf"
            :record-id="String(data.coldId || '')"
            folder-name="court-decisions"
          />
          <SourceExternalLink
            :source-url="String(data.officialSourceUrl || '')"
          />
        </template>
      </template>

      <CourtDecisionContent v-if="data" :data="data" />

      <template #footer>
        <JurisdictionReportBanner
          :jurisdiction-code="soleJurisdiction?.coldId ?? undefined"
          :jurisdiction-name="soleJurisdiction?.name ?? undefined"
        />
        <LastModified :date="data?.updatedAt" />
      </template>
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

    <EntityFeedback
      entity-type="court_decision"
      :entity-id="coldId"
      :entity-title="data?.caseTitle ?? undefined"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import CourtDecisionContent from "@/components/entity/content/CourtDecisionContent.vue";
import PdfLink from "@/components/ui/PdfLink.vue";
import SourceExternalLink from "@/components/sources/SourceExternalLink.vue";
import JurisdictionReportBanner from "@/components/jurisdiction/JurisdictionReportBanner.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import LastModified from "@/components/ui/LastModified.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/court-decision", coldId);

const soleJurisdiction = computed(() => {
  const jurisdictions = data.value?.relations.jurisdictions;
  if (jurisdictions?.length !== 1) return null;
  return jurisdictions[0];
});
</script>
