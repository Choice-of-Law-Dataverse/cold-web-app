<template>
  <div>
    <BaseDetailLayout
      :loading="isLoading"
      :result-data="processedAnswerData || {}"
      :labels="questionLabels"
      :tooltips="questionTooltips"
      :show-suggest-edit="true"
      :source-table="'Question'"
    >
      <!-- Custom rendering for Legal provision articles -->
      <template #domestic-legal-provisions="{ value }">
        <DetailRow
          :label="questionLabels['Domestic Legal Provisions']"
          :tooltip="questionTooltips['Domestic Legal Provisions']"
        >
          <QuestionSourceList
            :sources="
              [value || answerData?.['Domestic Legal Provisions']].filter(
                Boolean,
              )
            "
            :fallback-data="answerData"
            :fetch-oup-chapter="false"
            :fetch-primary-source="true"
          />
        </DetailRow>
      </template>

      <!-- Custom rendering for Court Decisions ID -->
      <template #court-decisions-id="{ value }">
        <DetailRow
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
          <RelatedLiterature
            :themes="processedAnswerData?.Themes"
            :literature-id="
              processedAnswerData?.['Jurisdictions Literature ID']
            "
            :jurisdiction="processedAnswerData?.Jurisdictions"
            :mode="'both'"
            :oup-filter="'onlyOup'"
          />
        </DetailRow>
      </template>

      <template #related-literature>
        <DetailRow
          :label="questionLabels['Related Literature']"
          :tooltip="questionTooltips['Related Literature']"
          variant="literature"
        >
          <RelatedLiterature
            :themes="processedAnswerData?.Themes"
            :literature-id="
              processedAnswerData?.['Jurisdictions Literature ID']
            "
            :jurisdiction="processedAnswerData?.Jurisdictions"
            :mode="'both'"
            :oup-filter="'noOup'"
          />
        </DetailRow>
      </template>

      <template #country-report>
        <CountryReportLink :jurisdiction-code="jurisdictionCode as string" />
      </template>
    </BaseDetailLayout>
    <QuestionJurisdictions
      v-if="questionSuffix"
      :question-suffix="questionSuffix"
    />

    <!-- Handle SEO meta tags -->
    <PageSeoMeta
      :title-candidates="[
        processedAnswerData?.Jurisdictions as string,
        processedAnswerData?.Question as string,
      ]"
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
import RelatedLiterature from "@/components/literature/RelatedLiterature.vue";
import QuestionSourceList from "@/components/sources/QuestionSourceList.vue";
import QuestionJurisdictions from "@/components/ui/QuestionJurisdictions.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useAnswer } from "@/composables/useAnswer";
import CountryReportLink from "~/components/ui/CountryReportLink.vue";
import { questionLabels } from "@/config/labels";
import { questionTooltips } from "@/config/tooltips";

const route = useRoute();

const { data: answerData, isLoading } = useAnswer(
  computed(() => route.params.id as string),
);

const processedAnswerData = computed(() => {
  if (!answerData.value) return null;

  const courtDecisionsId = answerData.value["Court Decisions ID"];

  return {
    ...answerData.value,
    "Domestic Legal Provisions":
      answerData.value["Domestic Legal Provisions"] || "",
    "Court Decisions ID":
      typeof courtDecisionsId === "string"
        ? courtDecisionsId.split(",").map((caseId: string) => caseId.trim())
        : [],
  };
});

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

const jurisdictionCode = computed(() => {
  return (
    processedAnswerData.value?.["Jurisdictions Alpha-3 code"] ||
    processedAnswerData.value?.["Jurisdictions Alpha-3 Code"]
  );
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
