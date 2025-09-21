<template>
  <main class="px-6">
    <div class="mx-auto w-full max-w-container">
      <!-- Header Section -->
      <GridContainer>
        <GridItem>
          <div class="mb-3 text-[60px] font-bold leading-[68px] md:text-left">
            Choice of Law<br />
            Dataverse
          </div>
        </GridItem>

        <GridItem>
          <h2
            class="mb-6 flex w-full flex-row items-center gap-1 pb-4 pt-4 text-xl font-medium md:text-left"
          >
            <span>
              Navigate private international law issues with precision.

              <UButton class="suggestion-button" to="/about" variant="link">
                <span>Read more </span>
              </UButton>
            </span>
          </h2>
        </GridItem>

        <GridItem>
          <JurisdictionMap />
        </GridItem>

        <GridItem>
          <CountrySelectMenu />
        </GridItem>

        <GridItem :mdCols="8">
          <SuccessfulLegalTransplantations />
        </GridItem>

        <GridItem :mdCols="4">
          <ConnectCard
            title="Transnational Standard"
            subtitle="Authoritative Instrument on Choice of Law"
            buttonText="HCCH Principles"
            buttonLink="/international-instrument/II-Pri-1"
            imageSrc="https://choiceoflaw.blob.core.windows.net/assets/hcch-logo-circle.svg"
            :newTab="false"
          />
        </GridItem>

        <GridItem :mdCols="4">
          <NumberCard
            title="Available Arbitral Awards"
            buttonText="See all"
            buttonLink="/arbitral-awards"
            tableName="Questions"
            :overrideNumber="74"
          />
        </GridItem>

        <GridItem :mdCols="4">
          <CompareJurisdictionsCard
            title="Compare Jurisdictions"
            buttonText="Go to comparison"
            iso3Left="CHE"
            iso3Right="CAN"
            :detectVisitorRight="true"
          />
        </GridItem>

        <GridItem :mdCols="4">
          <NumberCard
            title="Available Arbitral Rules"
            buttonText="See all"
            buttonLink="/arbitral-rules"
            tableName="Questions"
            :overrideNumber="37"
          />
        </GridItem>

        <GridItem :mdCols="6">
          <PopularSearches />
        </GridItem>

        <GridItem :cols="6">
          <TopLiteratureThemes />
        </GridItem>

        <GridItem :cols="4">
          <NumberCard
            title="Available Domestic Instruments"
            buttonText="See all"
            buttonLink="/search?type=Domestic+Instruments"
            tableName="Domestic Instruments"
          />
        </GridItem>

        <GridItem :mdCols="8">
          <RecentDomesticInstruments />
        </GridItem>

        <GridItem :mdCols="8">
          <PlotCourtDecisionsJurisdiction />
        </GridItem>

        <GridItem :mdCols="4">
          <NumberCard
            title="Available Court Decisions"
            buttonText="See all"
            buttonLink="/search?type=Court+Decisions"
            tableName="Court Decisions"
          />
        </GridItem>

        <GridItem :mdCols="8">
          <LeadingCases />
        </GridItem>

        <GridItem :mdCols="4">
          <ConnectCard
            title="CoLD Case Analyzer"
            buttonText="Analyze Court Cases with AI"
            :buttonLink="links.case_analyzer"
            iconName="i-material-symbols:chat-outline"
            buttonIcon="i-material-symbols:open-in-new"
          />
        </GridItem>

        <GridItem class="mb-4 flex justify-center">
          <ImportantQuestions
            :questionSuffixes="[
              '_01-P',
              '_03-PA',
              '_07-PA',
              '_09-FoC',
              '_13-TC',
              '_22-MR',
            ]"
          />
        </GridItem>

        <GridItem :cols="6" :mdCols="3">
          <ConnectCard
            title="CoLD Newsletter"
            buttonText="Subscribe"
            :buttonLink="links.substack"
            iconName="i-bi:substack"
            buttonIcon="i-material-symbols:open-in-new"
          />
        </GridItem>

        <GridItem :cols="6" :mdCols="3">
          <ConnectCard
            title="CoLD on LinkedIn"
            buttonText="Follow Us"
            :buttonLink="links.linkedin"
            iconName="i-mdi:linkedin"
            buttonIcon="i-material-symbols:open-in-new"
          />
        </GridItem>

        <GridItem :cols="6" :mdCols="3">
          <ConnectCard
            title="Questions, Feedback?"
            buttonText="Contact Us"
            buttonLink="/contact"
            :newTab="false"
            iconName="i-material-symbols:alternate-email"
          />
        </GridItem>

        <GridItem :cols="6" :mdCols="3">
          <ConnectCard
            title="Enter new Data"
            buttonText="Submit your data"
            buttonLink="/court-decision/new"
            iconName="i-material-symbols:add-notes"
            :newTab="false"
          />
        </GridItem>
      </GridContainer>
    </div>
  </main>
</template>

<script setup>
import PopularSearches from "@/components/landing-page/PopularSearches.vue";
import TopLiteratureThemes from "@/components/landing-page/TopLiteratureThemes.vue";
import JurisdictionMap from "@/components/landing-page/JurisdictionMap.vue";
import CountrySelectMenu from "@/components/landing-page/TempJurisdictionPicker.vue";
import PlotCourtDecisionsJurisdiction from "@/components/landing-page/PlotCourtDecisionsJurisdiction.vue";
import ConnectCard from "@/components/landing-page/ConnectCard.vue";
import NumberCard from "@/components/landing-page/NumberCard.vue";
import CompareJurisdictionsCard from "@/components/landing-page/CompareJurisdictionsCard.vue";
import { externalLinks } from "@/utils/externalLinks";
import RecentDomesticInstruments from "@/components/landing-page/RecentDomesticInstruments.vue";
import SuccessfulLegalTransplantations from "@/components/landing-page/SuccessfulLegalTransplantations.vue";
import LeadingCases from "@/components/landing-page/LeadingCases.vue";
import { useHead } from "#imports";
import ImportantQuestions from "~/components/landing-page/ImportantQuestions.vue";
import GridContainer from "@/components/layout/GridContainer.vue";
import GridItem from "@/components/layout/GridItem.vue";
const links = externalLinks;

useHead({
  title: "Choice of Law Dataverse — CoLD",
  link: [
    {
      rel: "canonical",
      href: "https://cold.global/",
    },
  ],
  meta: [
    {
      name: "description",
      content:
        "Choice of Law Dataverse — Navigate private international law issues with precision.",
    },
  ],
});
</script>

<style scoped>
h2 {
  font-weight: 500 !important;
}
</style>
