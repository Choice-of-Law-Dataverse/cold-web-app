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
      :title-candidates="[soleJurisdiction?.name, data?.question]"
      fallback="Question"
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
