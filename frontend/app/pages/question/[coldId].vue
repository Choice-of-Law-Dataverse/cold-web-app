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
      :field-order="entityConfig.fieldOrder"
      :label-overrides="entityConfig.labelOverrides"
      :tooltips="entityConfig.tooltips"
      :relations="answerData?.relations"
      :show-suggest-edit="true"
    >
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
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import JurisdictionReportBanner from "@/components/jurisdiction/JurisdictionReportBanner.vue";
import QuestionAnswerMap from "@/components/jurisdiction/QuestionAnswerMap.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { useAnswer } from "@/composables/useRecordDetails";
import { getEntityConfig } from "@/config/entityRegistry";

const entityConfig = getEntityConfig("/question")!;

const route = useRoute();
const answerId = ref(route.params.coldId as string);

const { data: answerData, isLoading, error } = useAnswer(answerId);

const primaryJurisdiction = computed(
  () => answerData.value?.relations.jurisdictions[0] ?? null,
);

const questionSuffix = computed(() => {
  const id = answerId.value;
  if (!id || typeof id !== "string") return null;

  const parts = id.split("_");
  if (parts.length > 1) {
    return "_" + parts.slice(1).join("_");
  }
  return "_" + id;
});
</script>
