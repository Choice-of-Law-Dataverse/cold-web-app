<template>
  <UApp>
    <NuxtLayout />
  </UApp>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { toAbsoluteUrl, toCanonicalPath } from "@/utils/seo";
import {
  buildJsonLdGraph,
  buildOrganization,
  buildWebSite,
} from "@/utils/structuredData";

const route = useRoute();
const config = useRuntimeConfig();

const siteUrl = computed(() => String(config.public.siteUrl ?? ""));

const canonicalUrl = computed(() =>
  toAbsoluteUrl(siteUrl.value, toCanonicalPath(route.path)),
);

const siteJsonLd = computed(() =>
  JSON.stringify(
    buildJsonLdGraph([
      buildOrganization(siteUrl.value),
      buildWebSite(siteUrl.value),
    ]),
  ),
);

useSeoMeta({
  description: "Choice of Law Dataverse",
  ogTitle: "Choice of Law Dataverse",
  ogDescription: "Navigate private international law issues with precision",
  ogImage: "https://assets.cold.global/assets/cold_og_image.svg",
  ogUrl: canonicalUrl,
  ogSiteName: "Choice of Law Dataverse",
  twitterTitle: "Choice of Law Dataverse",
  twitterDescription:
    "Navigate private international law issues with precision",
  twitterImage: "https://assets.cold.global/assets/cold_og_image.svg",
  twitterCard: "summary",
});

useHead({
  htmlAttrs: {
    lang: "en",
  },
  link: computed(() => [
    {
      rel: "canonical",
      href: canonicalUrl.value,
    },
    {
      rel: "preconnect",
      href: "https://assets.cold.global",
    },
    {
      rel: "stylesheet",
      href: "/print.css",
      media: "print",
    },
    {
      rel: "icon",
      type: "image/png",
      href: "/favicon-96x96.png",
      sizes: "96x96",
    },
    {
      rel: "icon",
      type: "image/svg+xml",
      href: "/favicon.svg",
    },
    {
      rel: "shortcut icon",
      href: "/favicon.ico",
    },
    {
      rel: "apple-touch-icon",
      sizes: "180x180",
      href: "/apple-touch-icon.png",
    },
    {
      rel: "manifest",
      href: "/site.webmanifest",
    },
  ]),
  meta: [{ name: "apple-mobile-web-app-title", content: "CoLD" }],
  script: [
    {
      key: "site-json-ld",
      type: "application/ld+json",
      innerHTML: siteJsonLd,
    },
  ],
});
</script>
