<template>
  <main class="px-6">
    <div class="mx-auto w-full max-w-container">
      <!-- Header Section -->
      <GridContainer>
        <GridItem>
          <div class="mb-3 text-[60px] font-bold leading-[68px] md:text-left">
            Choice of Law<br >
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

        <GridItem :md-cols="8">
          <SuccessfulLegalTransplantations />
        </GridItem>

        <GridItem :md-cols="4">
          <ConnectCard
            title="Transnational Standard"
            subtitle="Authoritative Instrument on Choice of Law"
            button-text="HCCH Principles"
            button-link="/international-instrument/II-Pri-1"
            image-src="https://choiceoflaw.blob.core.windows.net/assets/hcch-logo-circle.svg"
            :new-tab="false"
          />
        </GridItem>

        <GridItem :md-cols="4">
          <NumberCard
            title="Available Arbitral Awards"
            button-text="See all"
            button-link="/arbitral-awards"
            table-name="Questions"
            :override-number="74"
          />
        </GridItem>

        <GridItem :md-cols="4">
          <CompareJurisdictionsCard
            title="Compare Jurisdictions"
            button-text="Go to comparison"
            iso3-left="CHE"
            iso3-right="CAN"
            :detect-visitor-right="true"
          />
        </GridItem>

        <GridItem :md-cols="4">
          <NumberCard
            title="Available Arbitral Rules"
            button-text="See all"
            button-link="/arbitral-rules"
            table-name="Questions"
            :override-number="37"
          />
        </GridItem>

        <GridItem :md-cols="6">
          <PopularSearches />
        </GridItem>

        <GridItem :cols="6">
          <TopLiteratureThemes />
        </GridItem>

        <GridItem :cols="4">
          <NumberCard
            title="Available Domestic Instruments"
            button-text="See all"
            button-link="/search?type=Domestic+Instruments"
            table-name="Domestic Instruments"
          />
        </GridItem>

        <GridItem :md-cols="8">
          <RecentDomesticInstruments />
        </GridItem>

        <GridItem :md-cols="8">
          <ClientOnlyPlotCourtDecisions />
        </GridItem>

        <GridItem :md-cols="4">
          <NumberCard
            title="Available Court Decisions"
            button-text="See all"
            button-link="/search?type=Court+Decisions"
            table-name="Court Decisions"
          />
        </GridItem>

        <GridItem :md-cols="8">
          <LeadingCases />
        </GridItem>

        <GridItem :md-cols="4">
          <ConnectCard
            title="CoLD Case Analyzer"
            button-text="Analyze Court Cases with AI"
            :button-link="links.case_analyzer"
            icon-name="i-material-symbols:chat-outline"
            button-icon="i-material-symbols:open-in-new"
          />
        </GridItem>

        <GridItem class="mb-4 flex justify-center">
          <ImportantQuestions
            :question-suffixes="[
              '_01-P',
              '_03-PA',
              '_07-PA',
              '_09-FoC',
              '_13-TC',
              '_22-MR',
            ]"
          />
        </GridItem>

        <GridItem :cols="6" :md-cols="3">
          <ConnectCard
            title="CoLD Newsletter"
            button-text="Subscribe"
            :button-link="links.substack"
            icon-name="i-bi:substack"
            button-icon="i-material-symbols:open-in-new"
          />
        </GridItem>

        <GridItem :cols="6" :md-cols="3">
          <ConnectCard
            title="CoLD on LinkedIn"
            button-text="Follow Us"
            :button-link="links.linkedin"
            icon-name="i-mdi:linkedin"
            button-icon="i-material-symbols:open-in-new"
          />
        </GridItem>

        <GridItem :cols="6" :md-cols="3">
          <ConnectCard
            title="Questions, Feedback?"
            button-text="Contact Us"
            button-link="/contact"
            :new-tab="false"
            icon-name="i-material-symbols:alternate-email"
          />
        </GridItem>

        <GridItem :cols="6" :md-cols="3">
          <ConnectCard
            title="Enter new Data"
            button-text="Submit your data"
            button-link="/court-decision/new"
            icon-name="i-material-symbols:add-notes"
            :new-tab="false"
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
import ConnectCard from "@/components/landing-page/ConnectCard.vue";
import NumberCard from "@/components/landing-page/NumberCard.vue";
import CompareJurisdictionsCard from "@/components/landing-page/CompareJurisdictionsCard.vue";
import { externalLinks } from "@/utils/externalLinks";
import RecentDomesticInstruments from "@/components/landing-page/RecentDomesticInstruments.vue";
import SuccessfulLegalTransplantations from "@/components/landing-page/SuccessfulLegalTransplantations.vue";
import LeadingCases from "@/components/landing-page/LeadingCases.vue";
import { useHead } from "#imports";
import ImportantQuestions from "~/components/landing-page/ImportantQuestions.vue";

const PlotCourtDecisionsJurisdiction = defineAsyncComponent(() => 
  import("@/components/landing-page/PlotCourtDecisionsJurisdiction.vue")
);
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
