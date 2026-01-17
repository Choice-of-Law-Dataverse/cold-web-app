<template>
  <ContentPageLayout :nav-links="learnNavLinks">
    <ContentDoc path="/faq" />
  </ContentPageLayout>
</template>

<script setup>
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";
import { learnNavLinks } from "@/config/navigation";
</script>
