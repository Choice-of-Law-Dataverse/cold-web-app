<template>
  <div
    class="grid grid-cols-1 gap-x-4 gap-y-12 md:grid-cols-12 md:gap-x-6 md:gap-y-16"
  >
    <div class="animate-fade-scale-in col-span-12">
      <div
        class="hero-gradient hero-stack rounded-2xl px-3 py-8 md:px-10 md:py-14"
      >
        <h1
          class="hero-title text-[40px] leading-[1.02] font-bold text-pretty sm:text-[64px] md:text-[80px]"
        >
          Choice of Law Dataverse
        </h1>

        <div class="hero-bottom">
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
      </div>
    </div>

    <!-- Explore Data Stats Strip -->
    <div class="animate-fade-up animate-delay-1 col-span-12">
      <div class="grid grid-cols-2 gap-3 md:grid-cols-4 md:gap-3">
        <NumberCard
          title="Court Decisions"
          button-text="See all"
          button-link="/search?type=Court+Decisions"
          table-name="Court Decisions"
        />

        <NumberCard
          title="Domestic Instruments"
          button-text="See all"
          button-link="/search?type=Domestic+Instruments"
          table-name="Domestic Instruments"
        />

        <NumberCard
          title="Arbitral Awards"
          button-text="See all"
          button-link="/arbitral-award"
          table-name="Arbitral Awards"
        />

        <NumberCard
          title="Arbitral Rules"
          button-text="See all"
          button-link="/arbitral-rule"
          table-name="Arbitral Rules"
        />
      </div>
    </div>

    <div
      ref="mapMountTrigger"
      class="animate-fade-up animate-delay-3 col-span-12"
    >
      <ClientOnly>
        <JurisdictionMap v-if="shouldMountMap" />
        <div v-else class="map-ssr-placeholder" aria-hidden="true" />
        <template #fallback>
          <div class="map-ssr-placeholder" aria-hidden="true" />
        </template>
      </ClientOnly>
    </div>

    <!-- Contribute & Analyze Section -->
    <div class="animate-fade-up col-span-12">
      <section class="contribute-card">
        <div class="contribute-card__decor" aria-hidden="true">
          <div class="contribute-card__orb contribute-card__orb--purple" />
          <div class="contribute-card__orb contribute-card__orb--green" />
        </div>

        <div class="contribute-card__grid">
          <div class="contribute-card__intro">
            <span class="contribute-card__eyebrow">
              <Icon
                name="i-material-symbols:edit-document-outline"
                class="contribute-card__eyebrow-icon"
              />
              Contribute &amp; Analyze
            </span>
            <h2 class="contribute-card__title">
              Help grow the world&rsquo;s open record of choice of law.
            </h2>
            <p class="contribute-card__lead">
              Add a court decision, instrument, or scholarly work to the
              dataverse, or let our AI extract jurisdiction, governing-law
              clauses, and key PIL elements from a decision in seconds.
            </p>

            <div class="contribute-card__note">
              <div class="contribute-card__note-icon" aria-hidden="true">
                <Icon name="i-heroicons-lock-closed" />
              </div>
              <p>
                A free CoLD account is required to keep the dataverse
                trustworthy &mdash; we use it to prevent automated spam and
                preserve the integrity of every record. Sign-up takes under a
                minute.
              </p>
            </div>
          </div>

          <div class="contribute-card__actions">
            <NuxtLink to="/submit" class="contribute-card__action">
              <div class="contribute-card__action-icon">
                <Icon name="i-material-symbols:add-notes" />
              </div>
              <div class="contribute-card__action-body">
                <span class="contribute-card__action-title">
                  Submit new data
                </span>
                <span class="contribute-card__action-desc">
                  Court decisions, instruments &amp; literature
                </span>
              </div>
              <Icon
                name="i-material-symbols:arrow-forward-rounded"
                class="contribute-card__action-arrow"
              />
            </NuxtLink>

            <NuxtLink
              to="/court-decision/new"
              class="contribute-card__action contribute-card__action--featured"
            >
              <div class="contribute-card__action-icon">
                <Icon name="i-material-symbols:category-search-outline" />
              </div>
              <div class="contribute-card__action-body">
                <span class="contribute-card__action-pill">AI-powered</span>
                <span class="contribute-card__action-title">
                  Analyze a case
                </span>
                <span class="contribute-card__action-desc">
                  Auto-extract jurisdiction &amp; PIL elements
                </span>
              </div>
              <Icon
                name="i-material-symbols:arrow-forward-rounded"
                class="contribute-card__action-arrow"
              />
            </NuxtLink>
          </div>
        </div>
      </section>
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
      <StayConnectedCard />
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, onBeforeUnmount, onMounted, ref } from "vue";
import ConnectCard from "@/components/landing-page/ConnectCard.vue";
import NumberCard from "@/components/landing-page/NumberCard.vue";
import CompareJurisdictionsCard from "@/components/landing-page/CompareJurisdictionsCard.vue";
import StayConnectedCard from "@/components/landing-page/StayConnectedCard.vue";
import { useHead, useRuntimeConfig } from "#imports";

const JurisdictionMap = defineAsyncComponent(
  () => import("@/components/landing-page/JurisdictionMap.vue"),
);
const PopularSearches = defineAsyncComponent(
  () => import("@/components/landing-page/PopularSearches.vue"),
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

const config = useRuntimeConfig();

const mapMountTrigger = ref<HTMLElement | null>(null);
const shouldMountMap = ref(false);
let mapObserver: IntersectionObserver | null = null;

onMounted(() => {
  if (typeof IntersectionObserver === "undefined") {
    shouldMountMap.value = true;
    return;
  }
  const target = mapMountTrigger.value;
  if (!target) {
    shouldMountMap.value = true;
    return;
  }
  mapObserver = new IntersectionObserver(
    (entries) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        shouldMountMap.value = true;
        mapObserver?.disconnect();
        mapObserver = null;
      }
    },
    { rootMargin: "400px 0px" },
  );
  mapObserver.observe(target);
});

onBeforeUnmount(() => {
  mapObserver?.disconnect();
  mapObserver = null;
});

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

.hero-stack {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.hero-bottom {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
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

/* Contribute & Analyze section */
.contribute-card {
  position: relative;
  overflow: hidden;
  border-radius: 1rem;
  padding: 2rem 1.5rem;
  background:
    radial-gradient(
      circle at 0% 0%,
      color-mix(in srgb, var(--color-cold-purple) 7%, transparent),
      transparent 55%
    ),
    radial-gradient(
      circle at 100% 100%,
      color-mix(in srgb, var(--color-cold-green) 9%, transparent),
      transparent 55%
    ),
    color-mix(in srgb, white 92%, var(--color-cold-cream));
  border: 1px solid
    color-mix(in srgb, var(--color-cold-purple) 12%, transparent);
  box-shadow: 0 1px 3px 0 rgb(15 0 53 / 0.04);
}

@media (min-width: 768px) {
  .contribute-card {
    padding: 2.5rem 2.5rem;
  }
}

.contribute-card__decor {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  border-radius: inherit;
}

.contribute-card__orb {
  position: absolute;
  width: 18rem;
  height: 18rem;
  border-radius: 9999px;
  filter: blur(64px);
  opacity: 0.5;
}

.contribute-card__orb--purple {
  top: -6rem;
  left: -4rem;
  background: color-mix(in srgb, var(--color-cold-purple) 28%, transparent);
}

.contribute-card__orb--green {
  bottom: -6rem;
  right: -4rem;
  background: color-mix(in srgb, var(--color-cold-green) 36%, transparent);
}

.contribute-card__grid {
  position: relative;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 1024px) {
  .contribute-card__grid {
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
    gap: 3rem;
    align-items: center;
  }
}

.contribute-card__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-family: "DM Sans", sans-serif;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-cold-night-alpha);
}

.contribute-card__eyebrow-icon {
  font-size: 1rem;
  color: var(--color-cold-purple);
}

.contribute-card__title {
  font-family: "DM Sans", sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.01em;
  color: var(--color-cold-night);
  margin-top: 0.75rem;
  text-wrap: balance;
}

@media (min-width: 768px) {
  .contribute-card__title {
    font-size: 2.125rem;
  }
}

.contribute-card__lead {
  margin-top: 0.875rem;
  max-width: 36rem;
  font-family: "DM Sans", sans-serif;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--color-cold-night-alpha);
}

.contribute-card__note {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-top: 1.25rem;
  padding: 0.875rem 1rem;
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--color-cold-purple) 5%, white);
  border: 1px solid
    color-mix(in srgb, var(--color-cold-purple) 12%, transparent);
}

.contribute-card__note p {
  font-family: "DM Sans", sans-serif;
  font-size: 0.8125rem;
  line-height: 1.55;
  color: var(--color-cold-night-alpha);
}

.contribute-card__note-icon {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 9999px;
  background: color-mix(in srgb, var(--color-cold-purple) 12%, transparent);
  color: var(--color-cold-purple);
  font-size: 0.875rem;
}

.contribute-card__actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.contribute-card__action {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.125rem;
  border-radius: 0.875rem;
  background: white;
  border: 1px solid color-mix(in srgb, var(--color-cold-night) 8%, transparent);
  text-decoration: none;
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    box-shadow 180ms ease,
    background 180ms ease;
}

.contribute-card__action:hover {
  transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--color-cold-purple) 35%, transparent);
  box-shadow: 0 8px 24px -12px
    color-mix(in srgb, var(--color-cold-purple) 40%, transparent);
}

.contribute-card__action--featured {
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-purple) 6%, white),
    color-mix(in srgb, var(--color-cold-green) 8%, white)
  );
  border-color: color-mix(in srgb, var(--color-cold-purple) 22%, transparent);
}

.contribute-card__action-icon {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.75rem;
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--color-cold-purple) 14%, transparent),
    color-mix(in srgb, var(--color-cold-green) 18%, transparent)
  );
  color: var(--color-cold-purple);
  font-size: 1.375rem;
}

.contribute-card__action-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.contribute-card__action-pill {
  display: inline-flex;
  align-self: flex-start;
  align-items: center;
  padding: 0.125rem 0.5rem;
  margin-bottom: 0.25rem;
  border-radius: 9999px;
  background: color-mix(in srgb, var(--color-cold-purple) 12%, transparent);
  color: var(--color-cold-purple);
  font-family: "DM Sans", sans-serif;
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.contribute-card__action-title {
  font-family: "DM Sans", sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-cold-night);
  line-height: 1.3;
}

.contribute-card__action-desc {
  font-family: "DM Sans", sans-serif;
  font-size: 0.8125rem;
  font-weight: 400;
  color: var(--color-cold-slate);
  line-height: 1.4;
  margin-top: 0.125rem;
}

.contribute-card__action-arrow {
  flex-shrink: 0;
  font-size: 1.125rem;
  color: var(--color-cold-purple);
  transition: transform 180ms ease;
}

.contribute-card__action:hover .contribute-card__action-arrow {
  transform: translateX(3px);
}
</style>
