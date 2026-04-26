<template>
  <ContentPageLayout :nav-links="learnNavLinks">
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";
import { learnNavLinks } from "@/config/navigation";

useHead({
  title: "Data Sets — CoLD",
});

const { data: page } = await useAsyncData("data_sets", () =>
  queryCollection("content").path("/data_sets").first(),
);
</script>
