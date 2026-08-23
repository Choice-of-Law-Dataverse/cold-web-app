<template>
  <ContentPageLayout page-heading="Supporters">
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

useSeoMeta({
  title: "Supporters — CoLD",
  description:
    "The institutions and funders supporting the Choice of Law Dataverse, including the Swiss National Science Foundation.",
  ogTitle: "Supporters — CoLD",
  ogDescription:
    "The institutions and funders supporting the Choice of Law Dataverse, including the Swiss National Science Foundation.",
});

const { data: page } = await useAsyncData("supporters", () =>
  queryCollection("content").path("/supporters").first(),
);
</script>
