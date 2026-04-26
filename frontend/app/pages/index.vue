<template>
  <div
    class="grid grid-cols-1 gap-x-4 gap-y-12 md:grid-cols-12 md:gap-x-6 md:gap-y-16"
  >
    <div class="animate-fade-scale-in col-span-12">
      <div
        class="hero-gradient hero-grid rounded-2xl px-3 py-6 md:px-8 md:py-10"
      >
        <h1
          class="hero-title hero-grid-title text-[36px] leading-[1.05] font-bold text-pretty sm:text-[56px] md:text-[64px]"
        >
          Choice of Law Dataverse
        </h1>

        <div class="hero-grid-row2">
          <h2 class="hero-subtitle text-lg font-medium text-pretty">
            Navigate private international law issues with precision.
            <NuxtLink class="hero-link" to="/about" variant="link">
              What&nbsp;is&nbsp;CoLD?
            </NuxtLink>
          </h2>

          <UTooltip
            text="Winner of Swiss National ORD Prize 2025 for Legal Sciences"
          >
            <a
              href="https://ord.swiss-academies.ch/news/swiss-national-ord-prize-2025-for-legal-and-environmental-sciences"
              target="_blank"
              rel="noopener noreferrer"
              class="hero-badge"
            >
              <img
                src="https://assets.cold.global/assets/Prix-ORD-DEF_2025.png"
                alt="Swiss National ORD Prize 2025"
                class="hero-badge-img"
                width="64"
                height="67"
                loading="lazy"
                decoding="async"
              />
              <span class="hero-badge-text">Swiss National ORD Prize 2025</span>
            </a>
          </UTooltip>
        </div>

        <div class="hero-grid-actions">
          <HeroJurisdictionPicker
            v-if="jurisdictions"
            :jurisdictions="jurisdictions"
            @jurisdiction-selected="navigateToJurisdiction"
          />

          <NuxtLink to="/search" class="hero-action">
            <Icon name="i-material-symbols:search" class="hero-action-icon" />
            <span>
              <span class="hero-action-title">Search the database</span>
              <span class="hero-action-desc"
                >Court decisions, instruments, and literature</span
              >
            </span>
          </NuxtLink>

          <NuxtLink to="/court-decision/new" class="hero-action">
            <Icon
              name="i-material-symbols:category-search-outline"
              class="hero-action-icon"
            />
            <span>
              <span class="hero-action-title">Analyze a case</span>
              <span class="hero-action-desc"
                >AI-assisted court decision analysis</span
              >
            </span>
          </NuxtLink>
        </div>
      </div>
    </div>

    <div class="animate-fade-up animate-delay-1 col-span-12">
      <ClientOnly>
        <JurisdictionMap />
        <template #fallback>
          <div class="map-ssr-placeholder" aria-hidden="true" />
        </template>
      </ClientOnly>
    </div>

    <!-- Explore Data Section -->
    <div class="animate-fade-in animate-delay-3 col-span-12">
      <SectionHeader
        title="Explore Our Data"
        subtitle="Browse thousands of court decisions, instruments, and legal resources"
        icon="i-material-symbols:database-outline"
      />
    </div>

    <!-- Number Cards Grid -->
    <div class="animate-fade-up animate-delay-4 col-span-12">
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
          table-name="Arbitral Awards"
        />

        <NumberCard
          title="Available Arbitral Rules"
          button-text="See all"
          button-link="/arbitral-rule"
          table-name="Arbitral Rules"
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
        align="left"
      />
    </div>

    <div class="col-span-12 flex md:col-span-7">
      <ClientOnly>
        <RecentDomesticInstruments />
        <template #fallback>
          <div class="card-ssr-placeholder" aria-hidden="true" />
        </template>
      </ClientOnly>
    </div>

    <div class="col-span-12 flex md:col-span-5">
      <ClientOnly>
        <PopularSearches />
        <template #fallback>
          <div class="card-ssr-placeholder" aria-hidden="true" />
        </template>
      </ClientOnly>
    </div>

    <div class="col-span-12 flex md:col-span-7">
      <ClientOnly>
        <SuccessfulLegalTransplantations />
        <template #fallback>
          <div class="card-ssr-placeholder" aria-hidden="true" />
        </template>
      </ClientOnly>
    </div>

    <div class="col-span-12 flex md:col-span-5">
      <ConnectCard
        title="Transnational Standard"
        subtitle="Authoritative Instrument on Choice of Law"
        button-text="HCCH Principles"
        button-link="/international-instrument/II-Pri-1"
        image-src="https://assets.cold.global/assets/hcch-logo-circle.svg"
        :new-tab="false"
        :center-title="false"
        :show-top-border="true"
      />
    </div>

    <div class="col-span-12 flex md:col-span-7">
      <ClientOnly>
        <PlotCourtDecisionsJurisdiction />
        <template #fallback>
          <div class="card-ssr-placeholder" aria-hidden="true" />
        </template>
      </ClientOnly>
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
      <ClientOnly>
        <LeadingCases />
        <template #fallback>
          <div class="card-ssr-placeholder" aria-hidden="true" />
        </template>
      </ClientOnly>
    </div>

    <div class="col-span-12 flex md:col-span-5">
      <ClientOnly>
        <TopLiteratureThemes />
        <template #fallback>
          <div class="card-ssr-placeholder" aria-hidden="true" />
        </template>
      </ClientOnly>
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
        icon-name="i-simple-icons:substack"
        button-icon="i-material-symbols:open-in-new"
      />
    </div>

    <div class="col-span-6 md:col-span-4">
      <ConnectCard
        title="CoLD on LinkedIn"
        button-text="Follow Us"
        :button-link="links.linkedin"
        icon-name="i-simple-icons:linkedin"
        button-icon="i-material-symbols:open-in-new"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent } from "vue";
import HeroJurisdictionPicker from "@/components/landing-page/HeroJurisdictionPicker.vue";
import ConnectCard from "@/components/landing-page/ConnectCard.vue";
import NumberCard from "@/components/landing-page/NumberCard.vue";
import CompareJurisdictionsCard from "@/components/landing-page/CompareJurisdictionsCard.vue";
import SectionHeader from "@/components/ui/SectionHeader.vue";
import { externalLinks } from "@/utils/externalLinks";
import { useHead, useRuntimeConfig, useRouter } from "#imports";
import { useJurisdictions } from "@/composables/useJurisdictions";
import type { JurisdictionOption } from "@/types/analyzer";

const JurisdictionMap = defineAsyncComponent(
  () => import("@/components/landing-page/JurisdictionMap.vue"),
);
const PopularSearches = defineAsyncComponent(
  () => import("@/components/landing-page/PopularSearches.vue"),
);
const TopLiteratureThemes = defineAsyncComponent(
  () => import("@/components/landing-page/TopLiteratureThemes.vue"),
);
const RecentDomesticInstruments = defineAsyncComponent(
  () => import("@/components/landing-page/RecentDomesticInstruments.vue"),
);
const SuccessfulLegalTransplantations = defineAsyncComponent(
  () => import("@/components/landing-page/SuccessfulLegalTransplantations.vue"),
);
const LeadingCases = defineAsyncComponent(
  () => import("@/components/landing-page/LeadingCases.vue"),
);
const PlotCourtDecisionsJurisdiction = defineAsyncComponent(
  () => import("@/components/landing-page/PlotCourtDecisionsJurisdiction.vue"),
);

const links = externalLinks;
const config = useRuntimeConfig();
const router = useRouter();

const { data: jurisdictions } = useJurisdictions();

const navigateToJurisdiction = async (
  jurisdiction: JurisdictionOption | undefined,
) => {
  if (jurisdiction?.coldId) {
    await router.push(`/jurisdiction/${jurisdiction.coldId.toUpperCase()}`);
  }
};

useHead({
  title: "Choice of Law Dataverse — CoLD",
  link: [
    {
      rel: "canonical",
      href: `${config.public.siteUrl}/`,
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
.map-ssr-placeholder {
  width: 100%;
  height: 600px;
  border-radius: 1rem;
  background: var(--gradient-subtle);
}

@media (max-width: 640px) {
  .map-ssr-placeholder {
    height: 400px;
  }
}

.card-ssr-placeholder {
  width: 100%;
  min-height: 320px;
  border-radius: 0.75rem;
  background: var(--gradient-subtle);
}

h2 {
  font-weight: 500;
}

.hero-gradient {
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.05);
}

.hero-title {
  font-family: "DM Sans", sans-serif;
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
  color: var(--color-cold-purple);
  font-weight: 600;
  transition: color 0.2s ease;
  text-decoration: none;
}

.hero-link:hover {
  color: color-mix(in srgb, var(--color-cold-purple) 85%, #000);
  text-decoration: underline;
}

.hero-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 768px) {
  .hero-grid {
    display: grid;
    grid-template-columns: 1fr auto;
    grid-template-rows: auto auto;
    column-gap: 2.5rem;
    row-gap: 0.75rem;
  }

  .hero-grid-title {
    grid-column: 1;
    grid-row: 1;
    align-self: end;
  }

  .hero-grid-row2 {
    grid-column: 1;
    grid-row: 2;
    align-self: center;
  }

  .hero-grid-actions {
    grid-column: 2;
    grid-row: 1 / 3;
    align-self: center;
  }
}

.hero-grid-row2 {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.hero-grid-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  max-width: 340px;
  flex-shrink: 0;
}

.hero-action {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  background: color-mix(in srgb, white 60%, transparent);
  text-decoration: none;
  transition: all 0.15s ease;
}

.hero-action:hover {
  background: white;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.06);
}

.hero-action-icon {
  flex-shrink: 0;
  font-size: 1.125rem;
  color: var(--color-cold-purple);
}

.hero-action-title {
  display: block;
  font-family: "DM Sans", sans-serif;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-cold-night);
  line-height: 1.3;
}

.hero-action-desc {
  display: block;
  font-family: "DM Sans", sans-serif;
  font-size: 0.6875rem;
  font-weight: 400;
  color: var(--color-cold-slate);
  line-height: 1.3;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.625rem;
  text-decoration: none;
  opacity: 0.75;
  transition: opacity 0.15s ease;
}

.hero-badge:hover {
  opacity: 1;
}

.hero-badge-img {
  width: 64px;
  height: 67px;
}

.hero-badge-text {
  font-family: "DM Sans", sans-serif;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-cold-slate);
  letter-spacing: 0.02em;
}
</style>
