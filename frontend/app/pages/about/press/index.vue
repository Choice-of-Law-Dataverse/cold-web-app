<template>
  <ContentPageLayout>
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

useSeoMeta({
  title: "Press — CoLD",
  description:
    "Press coverage, announcements and media resources for the Choice of Law Dataverse.",
  ogTitle: "Press — CoLD",
  ogDescription:
    "Press coverage, announcements and media resources for the Choice of Law Dataverse.",
});

const { data: page } = await useAsyncData("press", () =>
  queryCollection("content").path("/press").first(),
);
</script>
