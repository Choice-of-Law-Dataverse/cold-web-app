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
import { buildDataset, buildJsonLdGraph } from "@/utils/structuredData";

useSeoMeta({
  title: "Data Sets — CoLD",
  description:
    "Download the Choice of Law Dataverse as open data sets, released under CC BY 4.0 for research and reuse.",
  ogTitle: "Data Sets — CoLD",
  ogDescription:
    "Download the Choice of Law Dataverse as open data sets, released under CC BY 4.0 for research and reuse.",
});

const { data: page } = await useAsyncData("data_sets", () =>
  queryCollection("content").path("/data_sets").first(),
);

const config = useRuntimeConfig();

useHead({
  script: [
    {
      key: "page-json-ld",
      type: "application/ld+json",
      innerHTML: computed(() =>
        JSON.stringify(
          buildJsonLdGraph([
            buildDataset(String(config.public.siteUrl ?? ""), {
              name: "Choice of Law Dataverse data sets",
              description:
                "Downloadable open data sets covering court decisions, domestic and international instruments, arbitral awards and jurisdiction reports on choice of law, released under CC BY 4.0.",
              path: "/learn/data-sets",
            }),
          ]),
        ),
      ),
    },
  ],
});
</script>
