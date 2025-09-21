<template>
  <ContentPageLayout :navLinks="learnNavLinks">
    <ContentDoc path="/data_sets" />
  </ContentPageLayout>
</template>

<script setup>
import ContentPageLayout from '@/components/layout/ContentPageLayout.vue'
import { learnNavLinks } from '@/config/pageConfigs.js'
</script>
