<template>
  <div>
    <h1 v-if="data?.question" class="sr-only">
      {{ data.question }}
    </h1>
    <BaseDetailLayout
      table="Questions"
      :loading="isLoading"
      :error="error"
      :data="data || {}"
      :show-suggest-edit="true"
    >
      <EntityContent base-path="/question" :data="data || {}" />

      <template #footer>
        <JurisdictionReportBanner
          :jurisdiction-code="
            (primaryJurisdiction?.coldId as string) ?? undefined
          "
          :jurisdiction-name="
            (primaryJurisdiction?.name as string) ?? undefined
          "
        />
        <LastModified :date="data?.updatedAt as string" />
      </template>
    </BaseDetailLayout>
    <div class="mt-8">
      <QuestionAnswerMap
        v-if="questionSuffix"
        :question-suffix="questionSuffix"
      />
    </div>

    <PageSeoMeta
      :title-candidates="[
        data?.jurisdictions as string,
        data?.question as string,
      ]"
      fallback="Question"
    />

    <EntityFeedback
      entity-type="question"
      :entity-id="answerId"
      :entity-title="data?.question as string"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import BaseDetailLayout from "@/components/layout/BaseDetailLayout.vue";
import EntityContent from "@/components/entity/EntityContent.vue";
import JurisdictionReportBanner from "@/components/jurisdiction/JurisdictionReportBanner.vue";
import QuestionAnswerMap from "@/components/jurisdiction/QuestionAnswerMap.vue";
import PageSeoMeta from "@/components/seo/PageSeoMeta.vue";
import EntityFeedback from "@/components/ui/EntityFeedback.vue";
import LastModified from "@/components/ui/LastModified.vue";
import { useEntityData } from "@/composables/useEntityData";

const route = useRoute();
const answerId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/question", answerId);

const primaryJurisdiction = computed(() => {
  const rels = data.value?.relations as
    | Record<string, Record<string, unknown>[]>
    | undefined;
  return rels?.jurisdictions?.[0] ?? null;
});

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
