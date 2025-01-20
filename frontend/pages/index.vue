<template>
  <main class="px-6">
    <div class="mx-auto" style="max-width: var(--container-width); width: 100%">
      <!-- Header Section -->
      <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
        <div class="col-span-12">
          <h1 class="text-3xl font-bold mb-3 md:text-left">
            Choice of Law Dataverse
          </h1>
          <h2 class="text-xl font-medium mb-6 md:text-left">
            Find relevant case law and choice of law answers for your case.
          </h2>
        </div>

        <!-- Popular Searches -->
        <div class="col-span-12">
          <PopularSearches />

          <JurisdictionMap />
          <CountrySelectMenu />
        </div>

        <div class="col-span-8">
          <PlotCourtDecisionsJurisdiction />
        </div>

        <!-- <div style="width: 33%">
        <ConnectCard
          title="CoLD Newsletter"
          buttonText="Subscribe on Substack"
          :buttonLink="links.substack"
          iconName="i-bi:substack"
        />
        <ConnectCard
          title="CoLD on LinkedIn"
          buttonText="Follow Us"
          :buttonLink="links.linkedin"
          iconName="i-mdi:linkedin"
        />
        <ConnectCard
          title="Questions? Feedback?"
          buttonText="Contact Us"
          buttonLink="/contact"
          :newTab="false"
          iconName="i-material-symbols:alternate-email"
        />
      </div>
    </div> -->
        <!-- </div> -->
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
</script>

<style scoped>
/* h1 {
  margin-bottom: 12px;
}

h2 {
  margin-bottom: 42px;
} */
</style>
