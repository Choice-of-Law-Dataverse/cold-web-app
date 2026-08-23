<template>
  <div>
    <BaseDetailLayout
      table="Questions"
      :page-heading="data?.question ?? ''"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
      entity-type="question"
      :entity-id="coldId"
      :entity-title="data?.question ?? undefined"
    >
      <QuestionContent v-if="data" :data="data" />
    </BaseDetailLayout>
    <div class="mt-8">
      <QuestionAnswerMap
        v-if="questionSuffix"
        :question-suffix="questionSuffix"
      />
    </div>

    <PageSeoMeta
      :title-candidates="[questionTitle, data?.question]"
      fallback="Question"
      :description-candidates="descriptionCandidates"
      :breadcrumbs="breadcrumbs"
      :noindex="isJurisdictionAnswer"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import QuestionContent from "@/components/entity/content/QuestionContent.vue";
import QuestionAnswerMap from "@/components/jurisdiction/QuestionAnswerMap.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/question", coldId);

const soleJurisdiction = computed(() => {
  const jurisdictions = data.value?.relations.jurisdictions;
  if (jurisdictions?.length !== 1) return null;
  return jurisdictions[0];
});

/**
 * Jurisdiction-specific answers are ~15k near-identical pages built from the
 * same 60 questions. They are kept crawlable so link equity reaches the
 * jurisdiction reports that aggregate them, but excluded from the index (and
 * from the sitemap) as thin content.
 */
const isJurisdictionAnswer = computed(() => coldId.value.includes("_"));

const questionTitle = computed(() =>
  soleJurisdiction.value?.name && data.value?.question
    ? `${data.value.question} — ${soleJurisdiction.value.name}`
    : (soleJurisdiction.value?.name ?? null),
);

const descriptionCandidates = computed(() => [
  data.value?.answer,
  soleJurisdiction.value?.name
    ? `Answer for ${soleJurisdiction.value.name} in the Choice of Law Dataverse.`
    : null,
  data.value?.moreInformation,
]);

const breadcrumbs = computed(() => {
  const trail = [{ name: "Home", path: "/" }];
  if (soleJurisdiction.value?.name && soleJurisdiction.value.coldId) {
    trail.push({
      name: soleJurisdiction.value.name,
      path: `/jurisdiction/${soleJurisdiction.value.coldId}`,
    });
  }
  trail.push({
    name: data.value?.question ?? "Question",
    path: `/question/${coldId.value}`,
  });
  return trail;
});

const questionSuffix = computed(() => {
  const id = coldId.value;
  if (!id || typeof id !== "string") return null;

  const parts = id.split("_");
  if (parts.length > 1) {
    return "_" + parts.slice(1).join("_");
  }
  return "_" + id;
});
</script>
