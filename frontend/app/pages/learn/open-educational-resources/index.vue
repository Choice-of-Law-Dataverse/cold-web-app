<template>
  <ContentPageLayout :nav-links="learnNavLinks">
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";
import { learnNavLinks } from "@/config/navigation";

useSeoMeta({
  title: "Open Educational Resources — CoLD",
  description:
    "Freely reusable teaching materials on choice of law and private international law, published under an open licence.",
  ogTitle: "Open Educational Resources — CoLD",
  ogDescription:
    "Freely reusable teaching materials on choice of law and private international law, published under an open licence.",
});

const { data: page } = await useAsyncData("open_educational_resources", () =>
  queryCollection("content").path("/open_educational_resources").first(),
);
</script>
