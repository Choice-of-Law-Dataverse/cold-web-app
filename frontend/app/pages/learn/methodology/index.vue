<template>
  <ContentPageLayout
    :nav-links="learnNavLinks"
    :enable-hierarchical-numbering="true"
  >
    <ContentRenderer v-if="intro" :value="intro" />
    <ContentRenderer v-if="questionnaireIntro" :value="questionnaireIntro" />
    <ContentRenderer v-if="questionnaire" :value="questionnaire" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";
import { learnNavLinks } from "@/config/navigation";

const { data: intro } = await useAsyncData("methodology_intro", () =>
  queryCollection("content").path("/methodology_intro").first(),
);

const { data: questionnaireIntro } = await useAsyncData(
  "methodology_questionnaire_intro",
  () =>
    queryCollection("content").path("/methodology_questionnaire_intro").first(),
);

const { data: questionnaire } = await useAsyncData(
  "methodology_questionnaire",
  () => queryCollection("content").path("/methodology_questionnaire").first(),
);
</script>
