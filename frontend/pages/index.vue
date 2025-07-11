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
        </div>

        <div class="col-span-12">
          <h2
            class="w-full text-xl font-medium mb-6 md:text-left pt-4 pb-4 flex flex-row items-center gap-1"
          >
            <span>
              Navigate private international law issues with precision.
              <UButton class="suggestion-button" to="/about" variant="link">
                <span>Read more</span>
              </UButton>
            </span>
          </h2>
        </div>

        <div class="col-span-12">
          <JurisdictionMap />
        </div>
        <div class="col-span-12">
          <CountrySelectMenu />
        </div>
        <div class="col-span-12 md:col-span-8">
          <SuccessfulLegalTransplantations />
        </div>
        <div class="col-span-12 sm:col-span-4">
          <ConnectCard
            title="Transnational Standard"
            subtitle="Authoritative Instrument on Choice of Law"
            buttonText="HCCH Principles"
            buttonLink="/international-instrument/II-HCC-1"
            imageSrc="https://choiceoflawdataverse.blob.core.windows.net/assets/hcch-logo-circle.svg"
            :newTab="false"
          />
        </div>

        <div class="col-span-12 md:col-span-6">
          <PopularSearches />
        </div>
        <div class="col-span-12 sm:col-span-6">
          <TopLiteratureThemes />
        </div>

        <div class="col-span-12 sm:col-span-4">
          <NumberCard
            title="Available Domestic Instruments"
            buttonText="See all"
            buttonLink="/search?type=Domestic+Instruments"
            tableName="Domestic Instruments"
          />
        </div>
        <div class="col-span-12 md:col-span-8">
          <RecentDomesticInstruments />
        </div>
        <div class="col-span-12 md:col-span-8">
          <PlotCourtDecisionsJurisdiction />
        </div>
        <div class="col-span-12 sm:col-span-4">
          <NumberCard
            title="Available Court Decisions"
            buttonText="See all"
            buttonLink="/search?type=Court+Decisions"
            tableName="Court Decisions"
          />
        </div>

        <div class="col-span-12">
          <LeadingCases />
        </div>

        <div class="col-span-12 sm:col-span-3">
          <ConnectCard
            title="CoLD Newsletter"
            buttonText="Subscribe"
            :buttonLink="links.substack"
            iconName="i-bi:substack"
            buttonIcon="i-material-symbols:open-in-new"
          />
        </div>

        <div class="col-span-12 sm:col-span-3">
          <ConnectCard
            title="CoLD on LinkedIn"
            buttonText="Follow Us"
            :buttonLink="links.linkedin"
            iconName="i-mdi:linkedin"
            buttonIcon="i-material-symbols:open-in-new"
          />
        </div>

        <div class="col-span-12 sm:col-span-3">
          <ConnectCard
            title="Questions, Feedback?"
            buttonText="Contact Us"
            buttonLink="/contact"
            :newTab="false"
            iconName="i-material-symbols:alternate-email"
          />
        </div>
        <div class="col-span-12 sm:col-span-3">
          <ConnectCard
            title="Access New Features"
            buttonText="Beta User Sign Up"
            :buttonLink="links.beta"
            iconName="i-hugeicons:test-tube-01"
            buttonIcon="i-material-symbols:open-in-new"
          />
        </div>
        <div class="col-span-12 sm:col-span-4">
          <ConnectCard
            title="Enter a new International Instrument"
            buttonText="Submit your data"
            buttonLink="/international-instrument/new"
            iconName="i-material-symbols:add-notes"
            :newTab="false"
          />
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import PopularSearches from '@/components/landing-page/PopularSearches.vue'
import TopLiteratureThemes from '@/components/landing-page/TopLiteratureThemes.vue'
import JurisdictionMap from '@/components/landing-page/JurisdictionMap.vue'
import CountrySelectMenu from '@/components/landing-page/TempJurisdictionPicker.vue'
import PlotCourtDecisionsJurisdiction from '@/components/landing-page/PlotCourtDecisionsJurisdiction.vue'
import ConnectCard from '@/components/landing-page/ConnectCard.vue'
import NumberCard from '@/components/landing-page/NumberCard.vue'
import { externalLinks } from '@/utils/externalLinks'
import RecentDomesticInstruments from '@/components/landing-page/RecentDomesticInstruments.vue'
import SuccessfulLegalTransplantations from '@/components/landing-page/SuccessfulLegalTransplantations.vue'
import LeadingCases from '@/components/landing-page/LeadingCases.vue'
import { useHead } from '#imports'
const links = externalLinks

useHead({
  title: 'Choice of Law Dataverse — CoLD',
  link: [
    {
      rel: 'canonical',
      href: 'https://cold.global/',
    },
  ],
  meta: [
    {
      name: 'description',
      content:
        'Choice of Law Dataverse — Navigate private international law issues with precision.',
    },
  ],
})
</script>

<style scoped>
h2 {
  font-weight: 500 !important;
}
</style>
