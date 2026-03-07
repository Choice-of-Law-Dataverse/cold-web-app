<template>
  <div>
    <h1 v-if="arbitralAward?.caseNumber" class="sr-only">
      Arbitral Award: {{ arbitralAward.caseNumber }}
    </h1>
    <BaseDetailLayout
      table="Arbitral Awards"
      :loading="loading"
      :error="error"
      :data="arbitralAward || {}"
      :labels="arbitralAwardLabels"
      :formatted-jurisdiction="
        arbitralAward?.formattedJurisdictions?.map((j) => j.Name) || []
      "
      :formatted-theme="
        arbitralAward?.formattedThemes?.map((t) => t.Theme) || []
      "
      :show-suggest-edit="true"
    >
      <template #footer>
        <LastModified :date="arbitralAward?.lastModified" />
      </template>
    </BaseDetailLayout>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[
        arbitralAward?.caseNumber && String(arbitralAward.caseNumber).trim()
          ? `Case Number ${arbitralAward.caseNumber}`
          : null,
      ]"
      fallback="Arbitral Award"
    />

    <EntityFeedback
      entity-type="arbitral_award"
      :entity-id="awardId"
      :entity-title="
        arbitralAward?.caseNumber
          ? `Case Number ${arbitralAward.caseNumber}`
          : undefined
      "
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import { useArbitralAward } from "@/composables/useRecordDetails";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { arbitralAwardLabels } from "@/config/labels";

const route = useRoute();

// Capture the ID once at setup to prevent flash during page transitions
const awardId = ref(route.params.id as string);

const {
  data: arbitralAward,
  isLoading: loading,
  error,
} = useArbitralAward(awardId);
</script>
