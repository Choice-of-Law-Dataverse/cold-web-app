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
        <section class="section-gap">
          <span class="label flex flex-row items-center">
            {{ keyLabelLookup.get("Domestic Legal Provisions")?.label || "Source fallback" }}
            <InfoPopover
              v-if="keyLabelLookup.get('Domestic Legal Provisions')?.tooltip"
              :text="keyLabelLookup.get('Domestic Legal Provisions')?.tooltip"
            />
          </span>
          <QuestionSourceList
            :sources="
              [
                ...(value || answerData?.['Domestic Legal Provisions']
                  ? [value || answerData?.['Domestic Legal Provisions']]
                  : []),
              ].filter(Boolean)
            "
            :fallback-data="answerData"
            :value-class-map="valueClassMap"
            :fetch-oup-chapter="true"
            :fetch-primary-source="true"
          />
        </section>
      </template>

      <!-- Custom rendering for Court Decisions ID -->
      <template #court-decisions-id="{ value }">
        <section id="related-court-decisions" class="section-gap">
          <span class="label flex flex-row items-center">
            {{ keyLabelLookup.get("Court Decisions ID")?.label || "Related Court Decisions" }}
            <InfoPopover
              v-if="keyLabelLookup.get('Court Decisions ID')?.tooltip"
              :text="keyLabelLookup.get('Court Decisions ID')?.tooltip"
            />
          </span>
          <CourtDecisionRenderer
            :value="value"
            :value-class-map="valueClassMap['Court Decisions ID']"
            :empty-value-behavior="
              keyLabelLookup.get('Domestic Legal Provisions')?.emptyValueBehavior
            "
          />
        </section>
      </template>

      <template #related-literature>
        <section class="section-gap">
          <RelatedLiterature
            :themes="processedAnswerData?.Themes"
            :literature-id="processedAnswerData?.['Jurisdictions Literature ID']"
            :mode="'both'"
            :value-class-map="valueClassMap['Related Literature']"
            :label="keyLabelLookup.get('Related Literature')?.label || 'Related Literature'"
            :empty-value-behavior="
              questionConfig.keyLabelPairs.find(
                (pair) => pair.key === 'Related Literature',
              )?.emptyValueBehavior
            "
            :tooltip="keyLabelLookup.get('Related Literature')?.tooltip"
          />
        </section>
      </template>
    </BaseDetailLayout>
    <CountryReportLink :processed-answer-data="processedAnswerData ?? {}" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, nextTick } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import CourtDecisionRenderer from "@/components/legal/CourtDecisionRenderer.vue";
import RelatedLiterature from "@/components/literature/RelatedLiterature.vue";
import QuestionSourceList from "@/components/sources/QuestionSourceList.vue";
import CountryReportLink from "@/components/ui/CountryReportLink.vue";
import InfoPopover from "~/components/ui/InfoPopover.vue";
import { useAnswer } from "@/composables/useAnswer";
import { questionConfig } from "@/config/pageConfigs";
import { useSeoMeta } from "#imports";

interface AnswerData {
  Question?: string;
  Jurisdictions?: string;
  Themes?: string;
  'Jurisdictions Literature ID'?: string;
  'Domestic Legal Provisions'?: string;
  'Court Decisions ID'?: string | string[];
  [key: string]: unknown;
}

const route = useRoute();

const { data: answerData, isLoading } = useAnswer(
  computed(() => route.params.id as string),
);

const { keyLabelPairs, valueClassMap } = questionConfig;

// Create lookup map for better performance
const keyLabelLookup = computed(() => {
  const map = new Map();
  keyLabelPairs.forEach(pair => {
    map.set(pair.key, pair);
  });
  return map;
});

// Preprocess data to handle custom rendering cases
const processedAnswerData = computed(() => {
  if (!answerData.value) return null;
  
  const courtDecisionsId = answerData.value["Court Decisions ID"];
  
  return {
    ...answerData.value,
    "Domestic Legal Provisions": (answerData.value["Domestic Legal Provisions"] as string) || "",
    "Court Decisions ID": typeof courtDecisionsId === 'string'
      ? courtDecisionsId.split(",").map((caseId: string) => caseId.trim())
      : [],
  } as AnswerData;
});

// Simplify page title generation
const pageTitle = computed(() => {
  if (!answerData.value) return "CoLD";
  
  const question = answerData.value.Question || "";
  const jurisdictions = answerData.value.Jurisdictions || "";
  
  if (question && jurisdictions) {
    return `${jurisdictions}: ${question} — CoLD`;
  } else if (question) {
    return `${question} — CoLD`;
  } else if (jurisdictions) {
    return `${jurisdictions} — CoLD`;
  }
  
  return "CoLD";
});

// Use useSeoMeta for better performance
useSeoMeta({
  title: pageTitle,
  description: pageTitle,
  ogTitle: pageTitle,
  ogDescription: pageTitle,
  twitterTitle: pageTitle,
  twitterDescription: pageTitle,
});

// Canonical URL
useHead({
  link: [
    {
      rel: "canonical",
      href: `https://cold.global${route.fullPath}`,
    },
  ],
});

onMounted(async () => {
  // Wait for the DOM to update then scroll if the hash is present
  await nextTick();
  if (window.location.hash === "#related-court-decisions") {
    const target = document.getElementById("related-court-decisions");
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  }
});
</script>
