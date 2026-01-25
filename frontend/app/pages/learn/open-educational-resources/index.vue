<template>
  <ContentPageLayout :nav-links="learnNavLinks">
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";
import { learnNavLinks } from "@/config/navigation";

const { data: page } = await useAsyncData("open_educational_resources", () =>
  queryCollection("content").path("/open_educational_resources").first(),
);
</script>
