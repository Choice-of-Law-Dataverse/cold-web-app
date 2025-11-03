<template>
  <div>
    <BaseDetailLayout
      :loading="isLoading"
      :result-data="processedAnswerData || {}"
      :key-label-pairs="keyLabelPairs"
      :value-class-map="valueClassMap"
      :show-suggest-edit="true"
      :source-table="'Question'"
    >
      <!-- Custom rendering for Legal provision articles -->
      <template #domestic-legal-provisions="{ value }">
        <DetailRow
          :label="
            keyLabelLookup.get('Domestic Legal Provisions')?.label ||
            'Source fallback'
          "
          :tooltip="keyLabelLookup.get('Domestic Legal Provisions')?.tooltip"
        >
          <QuestionSourceList
            :sources="
              [value || answerData?.['Domestic Legal Provisions']].filter(
                Boolean,
              )
            "
            :fallback-data="answerData"
            :value-class-map="valueClassMap"
            :fetch-oup-chapter="true"
            :fetch-primary-source="true"
          />
        </DetailRow>
      </template>

      <!-- Custom rendering for Court Decisions ID -->
      <template #court-decisions-id="{ value }">
        <DetailRow
          id="related-court-decisions"
          :label="
            keyLabelLookup.get('Court Decisions ID')?.label ||
            'Related Court Decisions'
          "
          :tooltip="keyLabelLookup.get('Court Decisions ID')?.tooltip"
        >
          <CourtDecisionRenderer
            :value="value"
            :value-class-map="valueClassMap['Court Decisions ID']"
            :empty-value-behavior="
              keyLabelLookup.get('Domestic Legal Provisions')
                ?.emptyValueBehavior
            "
          />
        </DetailRow>
      </template>

      <template #related-literature>
        <DetailRow
          :label="
            keyLabelLookup.get('Related Literature')?.label ||
            'Related Literature'
          "
          :tooltip="keyLabelLookup.get('Related Literature')?.tooltip"
        >
          <RelatedLiterature
            :themes="processedAnswerData?.Themes"
            :literature-id="
              processedAnswerData?.['Jurisdictions Literature ID']
            "
            :jurisdiction="processedAnswerData?.Jurisdictions"
            :mode="'both'"
            :value-class-map="valueClassMap['Related Literature']"
            :empty-value-behavior="
              questionConfig.keyLabelPairs.find(
                (pair) => pair.key === 'Related Literature',
              )?.emptyValueBehavior
            "
          />
        </DetailRow>
      </template>
    </BaseDetailLayout>
    <CountryReportLink :processed-answer-data="processedAnswerData ?? {}" />

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
import CountryReportLink from "@/components/ui/CountryReportLink.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useAnswer } from "@/composables/useAnswer";
import { questionConfig } from "@/config/pageConfigs";

interface AnswerData {
  Question?: string;
  Jurisdictions?: string;
  Themes?: string;
  "Jurisdictions Literature ID"?: string;
  "Domestic Legal Provisions"?: string;
  "Court Decisions ID"?: string | string[];
  [key: string]: unknown;
}

const route = useRoute();

const { data: answerData, isLoading } = useAnswer(
  computed(() => route.params.id as string),
);

const { keyLabelPairs, valueClassMap } = questionConfig;

const keyLabelLookup = computed(() => {
  const map = new Map();
  keyLabelPairs.forEach((pair) => {
    map.set(pair.key, pair);
  });
  return map;
});

const processedAnswerData = computed(() => {
  if (!answerData.value) return null;

  const courtDecisionsId = answerData.value["Court Decisions ID"];

  return {
    ...answerData.value,
    "Domestic Legal Provisions":
      (answerData.value["Domestic Legal Provisions"] as string) || "",
    "Court Decisions ID":
      typeof courtDecisionsId === "string"
        ? courtDecisionsId.split(",").map((caseId: string) => caseId.trim())
        : [],
  } as AnswerData;
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
