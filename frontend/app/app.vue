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

/**
 * ARD discovery link. `rel="ai-catalog"` is not in unhead's `Link` union, which
 * only models standard relations, so the cast is what lets it through.
 *
 * @see https://agenticresourcediscovery.org/
 */
const agentCatalogLink = {
  rel: "ai-catalog",
  type: "application/json",
  href: "/.well-known/ai-catalog.json",
} as unknown as { rel: "canonical"; href: string };

const siteJsonLd = computed(() =>
  JSON.stringify(
    buildJsonLdGraph([
      buildOrganization(siteUrl.value),
      buildWebSite(siteUrl.value),
    ]),
  ),
);

/**
 * Social platforms do not render SVG, so this has to stay a raster image.
 * Regenerate from `@/assets/og-image.svg` if the card design changes.
 */
const ogImageUrl = computed(() =>
  toAbsoluteUrl(siteUrl.value, "/og-image.png"),
);

useSeoMeta({
  description: "Choice of Law Dataverse",
  ogTitle: "Choice of Law Dataverse",
  ogDescription: "Navigate private international law issues with precision",
  ogImage: ogImageUrl,
  ogImageWidth: 1200,
  ogImageHeight: 630,
  ogImageType: "image/png",
  ogImageAlt:
    "Choice of Law Dataverse — navigate private international law issues with precision",
  ogUrl: canonicalUrl,
  ogSiteName: "Choice of Law Dataverse",
  twitterTitle: "Choice of Law Dataverse",
  twitterDescription:
    "Navigate private international law issues with precision",
  twitterImage: ogImageUrl,
  twitterImageAlt:
    "Choice of Law Dataverse — navigate private international law issues with precision",
  twitterCard: "summary_large_image",
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
    agentCatalogLink,
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
