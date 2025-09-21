<template>
  <ContentPageLayout :navLinks="learnNavLinks">
    <ContentDoc path="/glossary" />
  </ContentPageLayout>
</template>

<script setup>
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";
import { learnNavLinks } from "@/config/pageConfigs.js";
</script>
