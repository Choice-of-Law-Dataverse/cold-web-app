<template>
  <!-- Header Section -->
  <div class="grid grid-cols-1 gap-6 md:grid-cols-12">
    <div class="col-span-12">
      <div class="mb-3 text-[60px] font-bold leading-[68px] md:text-left">
        Choice of Law<br >
        Dataverse
      </div>
    </div>

    <div class="col-span-12">
      <div
        class="mb-6 flex w-full flex-col justify-between gap-2 pb-4 pt-4 sm:flex-row sm:items-center"
      >
        <h2 class="text-xl font-medium md:text-left">
          <span>
            Navigate private international law issues with precision.

            <NuxtLink class="suggestion-button" to="/about" variant="link">
              <span>Read more </span>
            </NuxtLink>
          </span>
        </h2>
        <OpenScienceBadge />
      </div>
    </div>

    <div class="col-span-12">
      <CountrySelectMenu />
    </div>

    <div class="col-span-12">
      <JurisdictionMap />
    </div>

    <!-- Number Cards Grid -->
    <div class="col-span-12">
      <div class="grid grid-cols-2 gap-6 md:grid-cols-4 md:gap-6">
        <NumberCard
          title="Available Court Decisions"
          button-text="See all"
          button-link="/search?type=Court+Decisions"
          table-name="Court Decisions"
        />

        <NumberCard
          title="Available Domestic Instruments"
          button-text="See all"
          button-link="/search?type=Domestic+Instruments"
          table-name="Domestic Instruments"
        />

        <NumberCard
          title="Available Arbitral Awards"
          button-text="See all"
          button-link="/arbitral-awards"
          table-name="Questions"
          :override-number="74"
        />

        <NumberCard
          title="Available Arbitral Rules"
          button-text="See all"
          button-link="/arbitral-rules"
          table-name="Questions"
          :override-number="37"
        />
      </div>
    </div>

    <div class="col-span-12 md:col-span-6">
      <ConnectCard
        title="Enter new Data"
        button-text="Submit your data"
        button-link="/submit"
        icon-name="i-material-symbols:add-notes"
        :new-tab="false"
      />
    </div>

    <div class="col-span-12 md:col-span-6">
      <ConnectCard
        title="CoLD Case Analyzer"
        button-text="Analyze Court Cases with AI"
        :button-link="links.case_analyzer"
        icon-name="i-material-symbols:chat-outline"
        button-icon="i-material-symbols:open-in-new"
      />
    </div>

    <div class="col-span-12 flex md:col-span-8">
      <RecentDomesticInstruments />
    </div>

    <div class="col-span-12 flex md:col-span-4">
      <PopularSearches />
    </div>

    <div class="col-span-12 flex md:col-span-8">
      <SuccessfulLegalTransplantations />
    </div>

    <div class="col-span-12 flex md:col-span-4">
      <ConnectCard
        title="Transnational Standard"
        subtitle="Authoritative Instrument on Choice of Law"
        button-text="HCCH Principles"
        button-link="/international-instrument/II-Pri-1"
        image-src="https://choiceoflaw.blob.core.windows.net/assets/hcch-logo-circle.svg"
        :new-tab="false"
      />
    </div>

    <div class="col-span-12 flex md:col-span-8">
      <PlotCourtDecisionsJurisdiction />
    </div>

    <div class="col-span-12 flex md:col-span-4">
      <CompareJurisdictionsCard
        title="Compare Jurisdictions"
        button-text="Go to comparison"
        iso3-left="CHE"
        iso3-right="CAN"
        :detect-visitor-right="true"
      />
    </div>
    <div class="col-span-12 flex md:col-span-8">
      <LeadingCases />
    </div>

    <div class="col-span-12 flex md:col-span-4">
      <TopLiteratureThemes />
    </div>

    <div class="col-span-12 mb-4 flex justify-center">
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
    </div>

    <div class="col-span-12 md:col-span-4">
      <ConnectCard
        title="Questions, Feedback?"
        button-text="Contact Us"
        button-link="/contact"
        :new-tab="false"
        icon-name="i-material-symbols:alternate-email"
      />
    </div>

    <div class="col-span-6 md:col-span-4">
      <ConnectCard
        title="CoLD Newsletter"
        button-text="Subscribe"
        :button-link="links.substack"
        icon-name="i-bi:substack"
        button-icon="i-material-symbols:open-in-new"
      />
    </div>

    <div class="col-span-6 md:col-span-4">
      <ConnectCard
        title="CoLD on LinkedIn"
        button-text="Follow Us"
        :button-link="links.linkedin"
        icon-name="i-mdi:linkedin"
        button-icon="i-material-symbols:open-in-new"
      />
    </div>
  </div>
</template>

<script setup>
import PopularSearches from "@/components/landing-page/PopularSearches.vue";
import TopLiteratureThemes from "@/components/landing-page/TopLiteratureThemes.vue";
import JurisdictionMap from "@/components/landing-page/JurisdictionMap.vue";
import CountrySelectMenu from "@/components/landing-page/TempJurisdictionPicker.vue";
import ConnectCard from "@/components/landing-page/ConnectCard.vue";
import NumberCard from "@/components/landing-page/NumberCard.vue";
import CompareJurisdictionsCard from "@/components/landing-page/CompareJurisdictionsCard.vue";
import OpenScienceBadge from "@/components/ui/OpenScienceBadge.vue";
import { externalLinks } from "@/utils/externalLinks";
import RecentDomesticInstruments from "@/components/landing-page/RecentDomesticInstruments.vue";
import SuccessfulLegalTransplantations from "@/components/landing-page/SuccessfulLegalTransplantations.vue";
import LeadingCases from "@/components/landing-page/LeadingCases.vue";
import { useHead } from "#imports";
import ImportantQuestions from "@/components/landing-page/ImportantQuestions.vue";
import PlotCourtDecisionsJurisdiction from "@/components/landing-page/PlotCourtDecisionsJurisdiction.vue";

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
