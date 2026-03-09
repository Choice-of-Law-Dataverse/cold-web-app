<template>
  <div>
    <h1 v-if="data?.question" class="sr-only">
      {{ data.question }}
    </h1>
    <BaseDetailLayout
      table="Questions"
      :loading="isLoading"
      :error="error"
      :data="data"
      :show-suggest-edit="true"
    >
      <EntityContent
        base-path="/question"
        :data="data || {}"
        :exclude-relations="excludedRelations"
      />

      <template #footer>
        <JurisdictionReportBanner
          :jurisdiction-code="soleJurisdiction?.coldId ?? undefined"
          :jurisdiction-name="soleJurisdiction?.name ?? undefined"
        />
        <LastModified :date="data?.updatedAt" />
      </template>
    </BaseDetailLayout>
    <div class="mt-8">
      <QuestionAnswerMap
        v-if="questionSuffix"
        :question-suffix="questionSuffix"
      />
    </div>

    <PageSeoMeta
      :title-candidates="[soleJurisdiction?.name, data?.question]"
      fallback="Question"
    />

    <EntityFeedback
      entity-type="question"
      :entity-id="coldId"
      :entity-title="data?.question ?? undefined"
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
const coldId = ref(route.params.coldId as string);

const { data, isLoading, error } = useEntityData("/question", coldId);

const excludedRelations = new Set(["questions"]);

const soleJurisdiction = computed(() => {
  const jurisdictions = data.value?.relations.jurisdictions;
  if (jurisdictions?.length !== 1) return null;
  return jurisdictions[0];
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
