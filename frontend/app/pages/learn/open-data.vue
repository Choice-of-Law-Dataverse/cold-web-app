<template>
  <ContentPageLayout page-heading="Open Data" :nav-links="learnNavLinks">
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";
import { learnNavLinks } from "@/config/navigation";

useSeoMeta({
  title: "Open Data — CoLD",
  description:
    "Comparative private international law research is fragmented and duplicated. CoLD makes its underlying data — decisions, legislation, literature — findable, accessible, interoperable, and reusable.",
  ogTitle: "Open Data — CoLD",
  ogDescription:
    "Legal sources as structured, openly licensed data — FAIR by design, across 100+ jurisdictions.",
});

const { data: page } = await useAsyncData("open_data", () =>
  queryCollection("content").path("/open_data").first(),
);
</script>
