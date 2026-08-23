<template>
  <ContentPageLayout>
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

useSeoMeta({
  title: "Endorsements — CoLD",
  description:
    "Endorsements of the Choice of Law Dataverse from scholars and institutions in private international law.",
  ogTitle: "Endorsements — CoLD",
  ogDescription:
    "Endorsements of the Choice of Law Dataverse from scholars and institutions in private international law.",
});

const { data: page } = await useAsyncData("endorsements", () =>
  queryCollection("content").path("/endorsements").first(),
);
</script>
