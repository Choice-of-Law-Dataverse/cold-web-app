<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <!-- Header Section -->
      <div class="col-span-12 grid grid-cols-1 md:grid-cols-12 gap-x-6">
        <div class="col-span-12">
          <div class="text-[60px] leading-[68px] font-bold mb-3 md:text-left">
            Choice of Law<br />
            Dataverse
          </div>
          <h2 class="text-xl font-medium mb-6 md:text-left pt-4 pb-4">
            Navigate private international law issues with precision.
            <UButton
              class="suggestion-button"
              to="/about"
              variant="link"
              icon="i-material-symbols:arrow-forward"
              trailing
            >
              <span>Learn more</span>
            </UButton>
          </h2>
        </div>

        <!-- Popular Searches -->
        <div class="col-span-12">
          <PopularSearches />
        </div>
        <div class="col-span-12">
          <JurisdictionMap />
        </div>
        <div class="col-span-12">
          <CountrySelectMenu />
        </div>

        <div class="col-span-12 md:col-span-8">
          <PlotCourtDecisionsJurisdiction />
        </div>

        <div class="col-span-12 sm:col-span-4">
          <ConnectCard
            title="CoLD Newsletter"
            buttonText="Subscribe on Substack"
            :buttonLink="links.substack"
            iconName="i-bi:substack"
          />
        </div>

        <div class="col-span-12 sm:col-span-4">
          <ConnectCard
            title="CoLD on LinkedIn"
            buttonText="Follow Us"
            :buttonLink="links.linkedin"
            iconName="i-mdi:linkedin"
          />
        </div>

        <div class="col-span-12 sm:col-span-4">
          <ConnectCard
            title="Questions? Feedback?"
            buttonText="Contact Us"
            buttonLink="/contact"
            :newTab="false"
            iconName="i-material-symbols:alternate-email"
          />
        </div>
        <div class="col-span-12 sm:col-span-4">
          <ConnectCard
            title="Access New Features"
            buttonText="Become a Beta Test User"
            :buttonLink="links.beta"
            iconName="i-material-symbols:cruelty-free"
          />
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import PopularSearches from '~/components/PopularSearches.vue'
import JurisdictionMap from '~/components/JurisdictionMap.vue'
import CountrySelectMenu from '~/components/TempJurisdictionPicker.vue'
import PlotCourtDecisionsJurisdiction from '~/components/PlotCourtDecisionsJurisdiction.vue'
import ConnectCard from '~/components/LandingPage/ConnectCard.vue'

import { externalLinks } from '~/utils/externalLinks'
const links = externalLinks

useSeoMeta({
  description: 'Choice of Law Dataverse',
  ogTitle: 'Choice of Law Dataverse',
  ogDescription: 'Navigate private international law issues with precision',
  ogImage:
    'https://choiceoflawdataverse.blob.core.windows.net/assets/cold_og_image.svg',
  ogUrl: 'www.cold.global',
  twitterTitle: 'Choice of Law Dataverse',
  twitterDescription:
    'Navigate private international law issues with precision',
  twitterImage:
    'https://choiceoflawdataverse.blob.core.windows.net/assets/cold_og_image.svg',
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
      href: 'https://choiceoflawdataverse.blob.core.windows.net/assets/favicon/favicon-96x96.png',
      sizes: '96x96',
    },
    {
      rel: 'icon',
      type: 'image/svg+xml',
      href: 'https://choiceoflawdataverse.blob.core.windows.net/assets/favicon/favicon.svg',
    },
    {
      rel: 'shortcut icon',
      href: 'https://choiceoflawdataverse.blob.core.windows.net/assets/favicon/favicon.ico',
    },
    {
      rel: 'apple-touch-icon',
      sizes: '180x180',
      href: 'https://choiceoflawdataverse.blob.core.windows.net/assets/favicon/apple-touch-icon.png',
    },
    {
      rel: 'manifest',
      href: 'https://choiceoflawdataverse.blob.core.windows.net/assets/favicon/site.webmanifest',
    },
  ],
  meta: [{ name: 'apple-mobile-web-app-title', content: 'CoLD' }],
})
</script>

<style scoped>
/* h1 {
  margin-bottom: 12px;
}

h2 {
  margin-bottom: 42px;
} */
</style>
