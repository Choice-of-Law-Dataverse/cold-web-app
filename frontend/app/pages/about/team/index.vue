<template>
  <ContentPageLayout>
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

useSeoMeta({
  title: "Team — CoLD",
  description:
    "The researchers and contributors behind the Choice of Law Dataverse.",
  ogTitle: "Team — CoLD",
  ogDescription:
    "The researchers and contributors behind the Choice of Law Dataverse.",
});

const { data: page } = await useAsyncData("team", () =>
  queryCollection("content").path("/team").first(),
);
</script>
