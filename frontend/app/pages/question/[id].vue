<template>
  <div>
    <BaseDetailLayout
      table="Questions"
      :loading="isLoading"
      :error="error"
      :data="answerData || {}"
      :labels="questionLabels"
      :tooltips="questionTooltips"
      :show-suggest-edit="true"
    >
      <!-- Custom rendering for Legal provision articles -->
      <template #domestic-legal-provisions>
        <DetailRow
          :label="questionLabels['Domestic Legal Provisions']"
          :tooltip="questionTooltips['Domestic Legal Provisions']"
        >
          <QuestionSourceList v-if="answerData" :data="answerData" />
        </DetailRow>
      </template>

      <!-- Custom rendering for Court Decisions ID -->
      <template #court-decisions-id="{ value }">
        <DetailRow
          v-if="value?.length"
          id="related-court-decisions"
          :label="questionLabels['Court Decisions ID']"
          :tooltip="questionTooltips['Court Decisions ID']"
          variant="court-decision"
        >
          <CourtDecisionRenderer :value="value" />
        </DetailRow>
      </template>

      <template #oup-chapter>
        <DetailRow :label="questionLabels['OUP Chapter']" variant="oup">
          <LazyRelatedLiterature
            hydrate-on-visible
            :themes="answerData?.Themes"
            :literature-id="answerData?.['Jurisdictions Literature ID']"
            :jurisdiction="answerData?.Jurisdictions"
            :mode="'both'"
            :oup-filter="'onlyOup'"
          />
        </DetailRow>
      </template>

      <template #related-literature>
        <DetailRow
          :label="questionLabels['Related Literature']"
          variant="literature"
        >
          <LazyRelatedLiterature
            hydrate-on-visible
            :themes="answerData?.Themes"
            :literature-id="answerData?.['Jurisdictions Literature ID']"
            :jurisdiction="answerData?.Jurisdictions"
            :mode="'both'"
            :oup-filter="'noOup'"
          />
        </DetailRow>
      </template>

      <template #footer>
        <LastModified :date="answerData?.['Last Modified']" />
        <LazyCountryReportBanner
          hydrate-on-visible
          :jurisdiction-code="answerData?.JurisdictionCode"
        />
      </template>
    </BaseDetailLayout>
    <QuestionJurisdictions
      v-if="questionSuffix"
      :question-suffix="questionSuffix"
    />

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[answerData?.Jurisdictions, answerData?.Question]"
      fallback="Question"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, nextTick } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import CourtDecisionRenderer from "@/components/legal/CourtDecisionRenderer.vue";
import QuestionSourceList from "@/components/sources/QuestionSourceList.vue";
import QuestionJurisdictions from "@/components/ui/QuestionJurisdictions.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useAnswer } from "@/composables/useRecordDetails";
import LastModified from "@/components/ui/LastModified.vue";
import { questionLabels } from "@/config/labels";
import { questionTooltips } from "@/config/tooltips";

const route = useRoute();

const {
  data: answerData,
  isLoading,
  error,
} = useAnswer(computed(() => route.params.id as string));

const questionSuffix = computed(() => {
  // Extract question suffix from the answer ID (route param)
  // Answer ID format: {ISO3_CODE}_{QUESTION_SUFFIX}
  const answerId = route.params.id as string;
  if (!answerId || typeof answerId !== "string") return null;

  const parts = answerId.split("_");
  if (parts.length > 1) {
    // Return everything after the first underscore (the question suffix)
    return "_" + parts.slice(1).join("_");
  }
  return null;
});

onMounted(async () => {
  await nextTick();
  if (window.location.hash === "#related-court-decisions") {
    const target = document.getElementById("related-court-decisions");
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  }
});
</script>
