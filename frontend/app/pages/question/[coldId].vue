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
      <template #domesticlegalprovisions>
        <DetailRow
          v-if="domesticInstrumentItems.length"
          :label="questionLabels.domesticLegalProvisions"
          :tooltip="questionTooltips.domesticLegalProvisions"
        >
          <RelatedItemsList
            :items="domesticInstrumentItems"
            base-path="/domestic-instrument"
          />
        </DetailRow>
      </template>

      <!-- Custom rendering for Court Decisions -->
      <template #courtdecisionsid>
        <DetailRow
          v-if="relatedCourtDecisions.length"
          id="related-court-decisions"
          :label="questionLabels.courtDecisionsId"
          :tooltip="questionTooltips.courtDecisionsId"
          variant="court-decision"
        >
          <RelatedItemsList
            :items="relatedCourtDecisions"
            base-path="/court-decision"
          />
        </DetailRow>
      </template>

      <template #relatedliterature>
        <DetailRow
          :label="questionLabels.relatedLiterature"
          variant="literature"
        >
          <RelatedItemsList
            :items="relatedLiterature"
            base-path="/literature"
            :empty-value-behavior="{ action: 'hide' }"
          />
        </DetailRow>
      </template>

      <template #footer>
        <JurisdictionReportBanner
          :jurisdiction-code="primaryJurisdiction?.coldId ?? undefined"
          :jurisdiction-name="primaryJurisdiction?.name ?? undefined"
        />
        <LastModified :date="answerData?.updatedAt" />
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
import { computed, onMounted, nextTick, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import DetailRow from "@/components/ui/DetailRow.vue";
import RelatedItemsList from "@/components/ui/RelatedItemsList.vue";
import JurisdictionReportBanner from "@/components/jurisdiction/JurisdictionReportBanner.vue";
import QuestionAnswerMap from "@/components/jurisdiction/QuestionAnswerMap.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { useAnswer } from "@/composables/useRecordDetails";
import { questionLabels } from "@/config/labels";
import { questionTooltips } from "@/config/tooltips";
import type { RelatedItem } from "@/types/ui";

const route = useRoute();
const answerId = ref(route.params.coldId as string);

const { data: answerData, isLoading, error } = useAnswer(answerId);

const primaryJurisdiction = computed(
  () => answerData.value?.relations.jurisdictions[0] ?? null,
);

const domesticInstrumentItems = computed<RelatedItem[]>(() =>
  (answerData.value?.relations.domesticInstruments ?? []).map((di) => ({
    id: di.coldId || String(di.id),
    title:
      di.abbreviation || di.titleInEnglish || di.officialTitle || String(di.id),
  })),
);

const relatedCourtDecisions = computed<RelatedItem[]>(() =>
  (answerData.value?.relations.courtDecisions ?? []).map((cd) => ({
    id: cd.coldId || String(cd.id),
    title: cd.caseTitle || cd.caseCitation || String(cd.id),
  })),
);

const relatedLiterature = computed<RelatedItem[]>(() =>
  (answerData.value?.relations.literature ?? []).map((lit) => ({
    id: lit.coldId || String(lit.id),
    title: lit.title || String(lit.id),
    ...(lit.oupJdChapter
      ? { badge: { label: "OUP", color: "var(--color-label-oup)" } }
      : {}),
  })),
);

const questionSuffix = computed(() => {
  const id = answerId.value;
  if (!id || typeof id !== "string") return null;

  const parts = id.split("_");
  if (parts.length > 1) {
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
