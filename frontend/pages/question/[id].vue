<template>
  <BaseDetailLayout
    :loading="isLoading"
    :resultData="processedAnswerData"
    :keyLabelPairs="keyLabelPairs"
    :valueClassMap="valueClassMap"
    :showSuggestEdit="true"
    :sourceTable="'Question'"
  >
    <!-- Custom rendering for Legal provision articles -->
    <template #domestic-legal-provisions="{ value }">
      <section class="section-gap">
        <span class="label flex flex-row items-center">
          {{
            keyLabelPairs.find(
              (pair) => pair.key === "Domestic Legal Provisions",
            )?.label || "Source fallback"
          }}
          <InfoPopover
            v-if="
              keyLabelPairs.find(
                (pair) => pair.key === 'Domestic Legal Provisions',
              )?.tooltip
            "
            :text="
              keyLabelPairs.find(
                (pair) => pair.key === 'Domestic Legal Provisions',
              )?.tooltip
            "
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
          :fallbackData="answerData"
          :valueClassMap="valueClassMap"
          :fetchOupChapter="true"
          :fetchPrimarySource="true"
        />
      </section>
    </template>

    <!-- Custom rendering for Court Decisions ID -->
    <template #court-decisions-id="{ value }">
      <section id="related-court-decisions" class="section-gap">
        <span class="label flex flex-row items-center">
          {{
            keyLabelPairs.find((pair) => pair.key === "Court Decisions ID")
              ?.label || "Related Court Decisions"
          }}
          <InfoPopover
            v-if="
              keyLabelPairs.find((pair) => pair.key === 'Court Decisions ID')
                ?.tooltip
            "
            :text="
              keyLabelPairs.find((pair) => pair.key === 'Court Decisions ID')
                ?.tooltip
            "
          />
        </span>
        <CourtDecisionRenderer
          :value="value"
          :valueClassMap="valueClassMap['Court Decisions ID']"
          :emptyValueBehavior="
            keyLabelPairs.find(
              (pair) => pair.key === 'Domestic Legal Provisions',
            )?.emptyValueBehavior
          "
        />
      </section>
    </template>

    <template #related-literature>
      <section class="section-gap">
        <RelatedLiterature
          :themes="processedAnswerData?.Themes"
          :literatureId="processedAnswerData?.['Jurisdictions Literature ID']"
          :mode="'both'"
          :valueClassMap="valueClassMap['Related Literature']"
          :label="
            keyLabelPairs.find((pair) => pair.key === 'Related Literature')
              ?.label || 'Related Literature'
          "
          :emptyValueBehavior="
            questionConfig.keyLabelPairs.find(
              (pair) => pair.key === 'Related Literature',
            )?.emptyValueBehavior
          "
          :tooltip="
            keyLabelPairs.find((pair) => pair.key === 'Related Literature')
              ?.tooltip
          "
        />
      </section>
    </template>
  </BaseDetailLayout>
  <CountryReportLink :processedAnswerData="processedAnswerData ?? {}" />
</template>

<script setup>
import { onMounted, nextTick, watch } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layouts/BaseDetailLayout.vue";
import CourtDecisionRenderer from "@/components/legal/CourtDecisionRenderer.vue";
import RelatedLiterature from "@/components/literature/RelatedLiterature.vue";
import QuestionSourceList from "@/components/sources/QuestionSourceList.vue";
import CountryReportLink from "@/components/ui/CountryReportLink.vue";
import InfoPopover from "~/components/ui/InfoPopover.vue";
import { useAnswer } from "@/composables/useAnswer";
import { questionConfig } from "@/config/pageConfigs";
import { useHead } from "#imports";

const route = useRoute();

const {
  data: answerData,
  isLoading,
  error,
} = useAnswer(computed(() => route.params.id));

const { keyLabelPairs, valueClassMap } = questionConfig;

// Preprocess data to handle custom rendering cases
const processedAnswerData = computed(() => {
  if (!answerData.value) return null;
  return {
    ...answerData.value,
    "Domestic Legal Provisions":
      answerData.value["Domestic Legal Provisions"] || "",
    "Court Decisions ID": answerData.value["Court Decisions ID"]
      ? answerData.value["Court Decisions ID"]
          .split(",")
          .map((caseId) => caseId.trim())
      : [],
  };
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

// Set dynamic page title: 'Jurisdictions: Question — CoLD'
watch(
  answerData,
  (newVal) => {
    if (!newVal) return;
    const question = newVal["Question"] || "";
    const jurisdictions = newVal["Jurisdictions"] || "";
    let pageTitle = "CoLD";
    if (question && jurisdictions) {
      pageTitle = `${jurisdictions}: ${question} — CoLD`;
    } else if (question) {
      pageTitle = `${question} — CoLD`;
    } else if (jurisdictions) {
      pageTitle = `${jurisdictions} — CoLD`;
    }
    useHead({
      title: pageTitle,
      link: [
        {
          rel: "canonical",
          href: `https://cold.global${route.fullPath}`,
        },
      ],
      meta: [
        {
          name: "description",
          content: pageTitle,
        },
      ],
    });
  },
  { immediate: true },
);
</script>
