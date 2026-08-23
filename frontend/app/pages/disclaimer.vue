<template>
  <ContentPageLayout page-heading="Disclaimer">
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

useSeoMeta({
  title: "Disclaimer — CoLD",
  description:
    "Terms of use and disclaimer for the Choice of Law Dataverse. The content is for research purposes and is not legal advice.",
  ogTitle: "Disclaimer — CoLD",
  ogDescription:
    "Terms of use and disclaimer for the Choice of Law Dataverse. The content is for research purposes and is not legal advice.",
});

const { data: page } = await useAsyncData("disclaimer", () =>
  queryCollection("content").path("/disclaimer").first(),
);
</script>
