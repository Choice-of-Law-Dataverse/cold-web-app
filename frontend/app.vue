<template>
  <div>
    <NuxtLayout />
    <UNotifications />
  </div>
</template>

<script setup>
import { useHead, useSeoMeta } from "@vueuse/head";

useSeoMeta({
  description: "Choice of Law Dataverse",
  ogTitle: "Choice of Law Dataverse",
  ogDescription: "Navigate private international law issues with precision",
  ogImage: "https://choiceoflaw.blob.core.windows.net/assets/cold_og_image.svg",
  ogUrl: "www.cold.global",
  twitterTitle: "Choice of Law Dataverse",
  twitterDescription:
    "Navigate private international law issues with precision",
  twitterImage:
    "https://choiceoflaw.blob.core.windows.net/assets/cold_og_image.svg",
  twitterCard: "summary",
});

useHead({
  htmlAttrs: {
    lang: "en",
  },
  link: [
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
  ],
  meta: [{ name: "apple-mobile-web-app-title", content: "CoLD" }],
});
</script>
