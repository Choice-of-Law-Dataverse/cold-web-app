<template>
  <div>
    <h1 v-if="answerData?.question" class="sr-only">
      {{ answerData.question }}
    </h1>
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
      <template #domesticlegalprovisions>
        <DetailRow
          :label="questionLabels.domesticLegalProvisions"
          :tooltip="questionTooltips.domesticLegalProvisions"
        >
          <QuestionSourceList v-if="answerData" :data="answerData" />
        </DetailRow>
      </template>

      <!-- Custom rendering for Court Decisions ID -->
      <template #courtdecisionsid="{ value }">
        <DetailRow
          v-if="value?.length"
          id="related-court-decisions"
          :label="questionLabels.courtDecisionsId"
          :tooltip="questionTooltips.courtDecisionsId"
          variant="court-decision"
        >
          <CourtDecisionRenderer :value="value" />
        </DetailRow>
      </template>

      <template #oupchapter>
        <DetailRow :label="questionLabels.oupChapter" variant="oup">
          <LazyRelatedLiterature
            :themes="answerData?.themes"
            :literature-id="answerData?.jurisdictionsLiteratureId"
            :jurisdiction="answerData?.jurisdictions"
            :mode="'both'"
            :oup-filter="'onlyOup'"
          />
        </DetailRow>
      </template>

      <template #relatedliterature>
        <DetailRow
          :label="questionLabels.relatedLiterature"
          variant="literature"
        >
          <LazyRelatedLiterature
            :themes="answerData?.themes"
            :literature-id="answerData?.jurisdictionsLiteratureId"
            :jurisdiction="answerData?.jurisdictions"
            :mode="'both'"
            :oup-filter="'noOup'"
          />
        </DetailRow>
      </template>

      <template #footer>
        <LastModified :date="answerData?.lastModified" />
        <LazyJurisdictionReportBanner
          :jurisdiction-code="answerData?.JurisdictionCode"
        />
      </template>
    </BaseDetailLayout>
    <div class="mt-8">
      <QuestionAnswerMap
        v-if="questionSuffix"
        :question-suffix="questionSuffix"
      />
    </div>

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[answerData?.jurisdictions, answerData?.question]"
      fallback="Question"
    />

    <EntityFeedback
      entity-type="question"
      :entity-id="answerId"
      :entity-title="answerData?.question as string"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, nextTick, defineAsyncComponent, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import CourtDecisionRenderer from "@/components/legal/CourtDecisionRenderer.vue";
import QuestionSourceList from "@/components/sources/QuestionSourceList.vue";
import QuestionAnswerMap from "@/components/jurisdiction/QuestionAnswerMap.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import { useAnswer } from "@/composables/useRecordDetails";
import LastModified from "@/components/ui/LastModified.vue";
import { questionLabels } from "@/config/labels";
import { questionTooltips } from "@/config/tooltips";

const LazyJurisdictionReportBanner = defineAsyncComponent(
  () => import("@/components/jurisdiction/JurisdictionReportBanner.vue"),
);
const LazyRelatedLiterature = defineAsyncComponent(
  () => import("@/components/literature/RelatedLiterature.vue"),
);

const route = useRoute();

// Capture the ID once at setup to prevent flash during page transitions
const answerId = ref(route.params.id as string);

const { data: answerData, isLoading, error } = useAnswer(answerId);

const questionSuffix = computed(() => {
  // Extract question suffix from the answer ID (route param)
  // Answer ID format: {ISO3_CODE}_{QUESTION_SUFFIX}
  const id = answerId.value;
  if (!id || typeof id !== "string") return null;

  const parts = id.split("_");
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
