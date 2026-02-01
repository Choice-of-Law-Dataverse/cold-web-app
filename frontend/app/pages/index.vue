<template>
  <div class="grid grid-cols-1 gap-4 md:grid-cols-12 md:gap-6">
    <div class="col-span-12">
      <div
        class="hero-gradient flex flex-col items-center justify-between gap-4 rounded-2xl px-3 py-4 md:flex-row md:px-6 md:py-12"
      >
        <div class="flex flex-col gap-4">
          <h1
            class="hero-title mb-2 text-[40px] leading-[1.1] font-bold text-pretty sm:mb-4 sm:text-[56px] md:text-[81px]"
          >
            Choice of Law Dataverse
          </h1>

          <div
            class="flex w-full flex-col justify-between gap-4 sm:flex-row sm:items-start"
          >
            <div class="flex flex-col gap-4">
              <h2
                class="hero-subtitle text-xl font-medium text-pretty md:text-left"
              >
                <span>
                  Navigate private international law issues with precision.

                  <NuxtLink class="hero-link" to="/about" variant="link">
                    <span>Read&nbsp;more</span>
                  </NuxtLink>
                </span>
              </h2>
              <div class="flex flex-wrap gap-3">
                <NuxtLink to="/search">
                  <UButton
                    size="lg"
                    class="hero-cta"
                    icon="i-material-symbols:search"
                  >
                    Start Exploring
                  </UButton>
                </NuxtLink>
                <NuxtLink to="/court-decision/new">
                  <UButton
                    size="lg"
                    variant="outline"
                    class="hero-cta-secondary"
                    icon="i-material-symbols:category-search-outline"
                  >
                    Analyze Case
                  </UButton>
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
        <div
          class="hidden min-w-[100px] items-center justify-center gap-3 sm:flex-col md:flex lg:flex-row"
        >
          <UTooltip
            text="Winner of Swiss National ORD Prize 2025 for Legal Sciences"
          >
            <a
              href="https://ord.swiss-academies.ch/news/swiss-national-ord-prize-2025-for-legal-and-environmental-sciences"
              target="_blank"
              rel="noopener noreferrer"
              class="transition-transform hover:scale-105"
            >
              <img
                src="https://choiceoflaw.blob.core.windows.net/assets/Prix-ORD-DEF_2025.png"
                alt="Swiss National ORD Prize 2025"
                style="width: 95px; height: 100px"
              />
            </a>
          </UTooltip>
        </div>
      </div>
    </div>

    <div class="col-span-12">
      <CountrySelectMenu />
    </div>

    <div class="col-span-12">
      <JurisdictionMap />
    </div>

    <!-- Explore Data Section -->
    <div class="col-span-12">
      <SectionHeader
        title="Explore Our Data"
        subtitle="Browse thousands of court decisions, instruments, and legal resources"
        icon="i-material-symbols:database-outline"
      />
    </div>

    <!-- Number Cards Grid -->
    <div class="col-span-12">
      <div class="grid grid-cols-2 gap-3 md:grid-cols-4 md:gap-4">
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
          button-link="/arbitral-award"
          table-name="Questions"
          :override-number="74"
        />

        <NumberCard
          title="Available Arbitral Rules"
          button-text="See all"
          button-link="/arbitral-rule"
          table-name="Questions"
          :override-number="37"
        />
      </div>
    </div>

    <!-- Contribute & Analyze Section -->
    <div class="col-span-12">
      <SectionHeader
        title="Contribute & Analyze"
        subtitle="Help grow the dataverse or use AI to analyze court cases"
        icon="i-material-symbols:edit-document-outline"
      />
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
        button-link="/court-decision/new"
        icon-name="i-material-symbols:category-search-outline"
      />
    </div>

    <!-- Featured Content Section -->
    <div class="col-span-12">
      <SectionHeader
        title="Featured Content"
        subtitle="Recent additions and popular searches in private international law"
        icon="i-material-symbols:star-outline"
      />
    </div>

    <div class="col-span-12 flex md:col-span-7">
      <RecentDomesticInstruments />
    </div>

    <div class="col-span-12 flex md:col-span-5">
      <PopularSearches />
    </div>

    <div class="col-span-12 flex md:col-span-7">
      <SuccessfulLegalTransplantations />
    </div>

    <div class="col-span-12 flex md:col-span-5">
      <ConnectCard
        title="Transnational Standard"
        subtitle="Authoritative Instrument on Choice of Law"
        button-text="HCCH Principles"
        button-link="/international-instrument/II-Pri-1"
        image-src="https://choiceoflaw.blob.core.windows.net/assets/hcch-logo-circle.svg"
        :new-tab="false"
        :center-title="false"
        :show-top-border="true"
      />
    </div>

    <div class="col-span-12 flex md:col-span-7">
      <PlotCourtDecisionsJurisdiction />
    </div>

    <div class="col-span-12 flex md:col-span-5">
      <CompareJurisdictionsCard
        title="Compare Jurisdictions"
        :comparisons="[
          { left: 'CHE', right: 'CAN' },
          { left: 'BRA', right: 'MOZ' },
          { left: 'EUR', right: 'GBR' },
          { left: 'USA', right: 'CHN' },
        ]"
      />
    </div>
    <div class="col-span-12 flex md:col-span-7">
      <LeadingCases />
    </div>

    <div class="col-span-12 flex md:col-span-5">
      <TopLiteratureThemes />
    </div>

    <!-- Stay Connected Section -->
    <div class="col-span-12">
      <SectionHeader
        title="Stay Connected"
        subtitle="Get in touch and stay updated with the latest from CoLD"
        icon="i-material-symbols:connect-without-contact"
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
// import OpenScienceBadge from "@/components/ui/OpenScienceBadge.vue";
// import HCCHApproved from "@/components/ui/HCCHApproved.vue";
import SectionHeader from "@/components/ui/SectionHeader.vue";
import { externalLinks } from "@/utils/externalLinks";
import RecentDomesticInstruments from "@/components/landing-page/RecentDomesticInstruments.vue";
import SuccessfulLegalTransplantations from "@/components/landing-page/SuccessfulLegalTransplantations.vue";
import LeadingCases from "@/components/landing-page/LeadingCases.vue";
import { useHead } from "#imports";
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

.hero-gradient {
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.05);
}

.hero-title {
  background: linear-gradient(
    135deg,
    var(--color-cold-night),
    var(--color-cold-purple),
    var(--color-cold-green)
  );
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  color: color-mix(in srgb, var(--color-cold-night) 85%, transparent);
}

.hero-link {
  color: var(--color-cold-purple) !important;
  font-weight: 600 !important;
  transition: color 0.2s ease;
  text-decoration: none !important;
}

.hero-link:hover {
  color: color-mix(in srgb, var(--color-cold-purple) 85%, #000) !important;
  text-decoration: underline !important;
}

.hero-cta {
  background: linear-gradient(
    135deg,
    var(--color-cold-purple),
    var(--color-cold-teal)
  ) !important;
  color: white !important;
  font-weight: 600 !important;
  border: none !important;
  transition: all 0.2s ease !important;
  box-shadow:
    0 4px 6px -1px rgb(0 0 0 / 0.1),
    0 2px 4px -2px rgb(0 0 0 / 0.1) !important;
}

.hero-cta:hover {
  transform: translateY(-2px);
  box-shadow:
    0 10px 15px -3px rgb(0 0 0 / 0.1),
    0 4px 6px -4px rgb(0 0 0 / 0.1) !important;
}

.hero-cta-secondary {
  border-color: var(--color-cold-purple) !important;
  color: var(--color-cold-purple) !important;
  font-weight: 600 !important;
  transition: all 0.2s ease !important;
}

.hero-cta-secondary:hover {
  background: color-mix(
    in srgb,
    var(--color-cold-purple) 8%,
    transparent
  ) !important;
  transform: translateY(-2px);
}
</style>
