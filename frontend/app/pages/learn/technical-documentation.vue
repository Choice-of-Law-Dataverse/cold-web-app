<template>
  <ContentPageLayout
    page-heading="Technical documentation"
    :nav-links="learnNavLinks"
  >
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";
import { learnNavLinks } from "@/config/navigation";

useSeoMeta({
  title: "Technical Documentation — CoLD",
  description:
    "Architecture, data model, public API, search behavior, technology stack, and deployment of the Choice of Law Dataverse.",
  ogTitle: "Technical Documentation — CoLD",
  ogDescription:
    "Architecture, data model, public API, search behavior, technology stack, and deployment of the Choice of Law Dataverse.",
});

const { data: page } = await useAsyncData("technical_documentation", () =>
  queryCollection("content").path("/technical_documentation").first(),
);
</script>
