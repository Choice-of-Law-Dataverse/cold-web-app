<template>
  <ContentPageLayout>
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";

useSeoMeta({
  title: "Contact — CoLD",
  description:
    "Get in touch with the Choice of Law Dataverse team about the data, contributions or collaboration.",
  ogTitle: "Contact — CoLD",
  ogDescription:
    "Get in touch with the Choice of Law Dataverse team about the data, contributions or collaboration.",
});

const { data: page } = await useAsyncData("contact", () =>
  queryCollection("content").path("/contact").first(),
);
</script>
