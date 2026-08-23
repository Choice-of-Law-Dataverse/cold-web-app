<template>
  <ContentPageLayout :nav-links="learnNavLinks">
    <ContentRenderer v-if="page" :value="page" />
  </ContentPageLayout>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useHead, useRuntimeConfig, useSeoMeta } from "#imports";
import ContentPageLayout from "@/components/layout/ContentPageLayout.vue";
import { learnNavLinks } from "@/config/navigation";
import { buildDefinedTermSet, buildJsonLdGraph } from "@/utils/structuredData";
import { extractHeadingSections, type ContentNode } from "@/utils/contentAst";

useSeoMeta({
  title: "Glossary — CoLD",
  description:
    "Definitions of the private international law terms used throughout the Choice of Law Dataverse, from party autonomy to renvoi and the public policy exception.",
  ogTitle: "Glossary — CoLD",
  ogDescription:
    "Definitions of the private international law terms used throughout the Choice of Law Dataverse, from party autonomy to renvoi and the public policy exception.",
});

const { data: page } = await useAsyncData("glossary", () =>
  queryCollection("content").path("/glossary").first(),
);

const config = useRuntimeConfig();

const glossaryJsonLd = computed(() => {
  const sections = extractHeadingSections(
    page.value?.body?.value as ContentNode[] | undefined,
  );
  const node = buildDefinedTermSet(
    String(config.public.siteUrl ?? ""),
    "/learn/glossary",
    sections.map((section) => ({
      term: section.heading,
      definition: section.text,
    })),
  );
  return node ? JSON.stringify(buildJsonLdGraph([node])) : "";
});

useHead({
  script: computed(() =>
    glossaryJsonLd.value
      ? [
          {
            key: "page-json-ld",
            type: "application/ld+json",
            innerHTML: glossaryJsonLd.value,
          },
        ]
      : [],
  ),
});
</script>
