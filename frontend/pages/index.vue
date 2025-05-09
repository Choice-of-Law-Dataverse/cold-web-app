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

        <div class="col-span-12">
          <PopularSearches />
        </div>
        <div class="col-span-12">
          <JurisdictionMap />
        </div>
        <div class="col-span-12">
          <CountrySelectMenu />
        </div>
        <div class="col-span-8">
          <RecentDomesticInstruments />
        </div>
        <div class="col-span-12 sm:col-span-4 flex flex-col gap-x-6">
          <NumberCard
            title="Available Court Decisions"
            buttonText="See all"
            buttonLink="/search?type=Court+Decisions"
            tableName="Court Decisions"
          />
          <NumberCard
            title="Available Domestic Instruments"
            buttonText="See all"
            buttonLink="/search?type=Domestic+Instruments"
            tableName="Domestic Instruments"
          />
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
            iconName="i-hugeicons:test-tube-01"
          />
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import PopularSearches from '~/components/landing-page/PopularSearches.vue'
import JurisdictionMap from '~/components/landing-page/JurisdictionMap.vue'
import CountrySelectMenu from '~/components/landing-page/TempJurisdictionPicker.vue'
import PlotCourtDecisionsJurisdiction from '~/components/landing-page/PlotCourtDecisionsJurisdiction.vue'
import ConnectCard from '~/components/landing-page/ConnectCard.vue'
import NumberCard from '~/components/landing-page/NumberCard.vue'
import { externalLinks } from '~/utils/externalLinks'
import RecentDomesticInstruments from '~/components/landing-page/RecentDomesticInstruments.vue'
// import LoadingLandingPageCard from '~/components/layout/LoadingLandingPageCard.vue'
const links = externalLinks
</script>
