<template>
  <ContentPageLayout :nav-links="learnNavLinks">
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useHead, useSeoMeta } from "#imports";
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";
import { learnNavLinks } from "@/config/navigation";
import { buildFaqPage, buildJsonLdGraph } from "@/utils/structuredData";
import { extractHeadingSections, type ContentNode } from "@/utils/contentAst";

useSeoMeta({
  title: "FAQ — CoLD",
  description:
    "Answers to common questions about the Choice of Law Dataverse: what it covers, how the data is produced, and how to cite and reuse it.",
  ogTitle: "FAQ — CoLD",
  ogDescription:
    "Answers to common questions about the Choice of Law Dataverse: what it covers, how the data is produced, and how to cite and reuse it.",
});

const { data: page } = await useAsyncData("faq", () =>
  queryCollection("content").path("/faq").first(),
);

const faqJsonLd = computed(() => {
  const sections = extractHeadingSections(
    page.value?.body?.value as ContentNode[] | undefined,
  );
  const node = buildFaqPage(
    sections.map((section) => ({
      question: section.heading,
      answer: section.text,
    })),
  );
  return node ? JSON.stringify(buildJsonLdGraph([node])) : "";
});

useHead({
  script: computed(() =>
    faqJsonLd.value
      ? [
          {
            key: "page-json-ld",
            type: "application/ld+json",
            innerHTML: faqJsonLd.value,
          },
        ]
      : [],
  ),
});
</script>
