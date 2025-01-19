<template>
  <div class="container">
    <div class="col-span-12">
      <h1>Choice of Law Dataverse</h1>
      <h2>Find relevant case law and choice of law answers for your case.</h2>
      <PopularSearches />
      <JurisdictionMap />
      <!-- <CountrySelectMenu /> -->
      <div style="width: 60%">
        <PlotCourtDecisionsJurisdiction />
      </div>
      <div style="width: 33%">
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
    </div>
  </div>
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
h1 {
  margin-bottom: 12px;
}

h2 {
  margin-bottom: 42px;
}
</style>
