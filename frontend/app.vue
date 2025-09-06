<template>
  <NuxtLayout>
    <NuxtPage />
    <CookieConsentBanner />
  </NuxtLayout>
</template>

<script setup>
import CookieConsentBanner from '@/components/ui/CookieConsentBanner.vue'

useSeoMeta({
  description: 'Choice of Law Dataverse',
  ogTitle: 'Choice of Law Dataverse',
  ogDescription: 'Navigate private international law issues with precision',
  ogImage: 'https://choiceoflaw.blob.core.windows.net/assets/cold_og_image.svg',
  ogUrl: 'www.cold.global',
  twitterTitle: 'Choice of Law Dataverse',
  twitterDescription:
    'Navigate private international law issues with precision',
  twitterImage:
    'https://choiceoflaw.blob.core.windows.net/assets/cold_og_image.svg',
  twitterCard: 'summary',
})

useHead({
  htmlAttrs: {
    lang: 'en',
  },
  link: [
    {
      rel: 'icon',
      type: 'image/png',
      href: 'https://choiceoflaw.blob.core.windows.net/assets/favicon/favicon-96x96.png',
      sizes: '96x96',
    },
    {
      rel: 'icon',
      type: 'image/svg+xml',
      href: 'https://choiceoflaw.blob.core.windows.net/assets/favicon/favicon.svg',
    },
    {
      rel: 'shortcut icon',
      href: 'https://choiceoflaw.blob.core.windows.net/assets/favicon/favicon.ico',
    },
    {
      rel: 'apple-touch-icon',
      sizes: '180x180',
      href: 'https://choiceoflaw.blob.core.windows.net/assets/favicon/apple-touch-icon.png',
    },
    {
      rel: 'manifest',
      href: 'https://choiceoflaw.blob.core.windows.net/assets/favicon/site.webmanifest',
    },
  ],
  meta: [{ name: 'apple-mobile-web-app-title', content: 'CoLD' }],
})
</script>
