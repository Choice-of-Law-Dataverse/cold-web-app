<template>
  <ContentPageLayout
    :nav-links="learnNavLinks"
    :enable-hierarchical-numbering="true"
  >
    <ContentDoc path="/methodology_intro" />
    <ContentDoc path="/methodology_questionnaire_intro" />
    <ContentDoc path="/methodology_questionnaire" />
  </ContentPageLayout>
</template>

<script setup>
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";
import { learnNavLinks } from "@/config/pageConfigs.js";
</script>
