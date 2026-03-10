<template>
  <div class="mx-auto max-w-4xl px-4 py-10 sm:px-6">
    <div
      class="border-cold-gray relative overflow-hidden border bg-white shadow-lg"
    >
      <div
        class="from-cold-purple to-cold-purple absolute inset-x-0 top-0 h-1 bg-gradient-to-r via-[#9b93e8]"
      />

      <div class="px-6 pt-14 pb-8 sm:px-16">
        <div class="border-cold-gray border-b pb-8 text-center">
          <p
            class="text-cold-purple text-xs font-medium tracking-[3px] uppercase"
          >
            Online via Zoom &middot; Free &amp; Open
          </p>
          <h1
            class="text-cold-night mt-4 font-serif text-4xl leading-tight font-bold sm:text-5xl"
          >
            Choice of Law Dataverse in Action
          </h1>
          <p class="text-cold-charcoal mt-3 text-base font-light">
            Launch Event &middot;
            <a
              href="https://www.cold.global/"
              target="_blank"
              class="text-cold-charcoal font-light underline underline-offset-2"
              >cold.global</a
            >
          </p>
          <div class="mt-5 flex flex-wrap items-center justify-center gap-3">
            <span
              class="border-cold-purple text-cold-night inline-block border px-5 py-2 text-xs font-medium tracking-[1.5px] uppercase"
            >
              28 April 2026 &middot; 11.30 am – 7.00 pm CEST
            </span>
            <a
              :href="zoomUrl"
              target="_blank"
              class="text-cold-purple inline-flex items-center gap-1.5 rounded-sm border border-[#ebe9f8] bg-[#ebe9f8] px-4 py-2 text-xs font-medium tracking-wide transition-colors hover:border-[#d8d4f5] hover:bg-[#d8d4f5]"
            >
              <Icon name="lucide:video" class="size-3.5" />
              Join Zoom
            </a>
            <a
              :href="calendarUrl"
              target="_blank"
              class="text-cold-purple inline-flex items-center gap-1.5 rounded-sm border border-[#ebe9f8] bg-[#ebe9f8] px-4 py-2 text-xs font-medium tracking-wide transition-colors hover:border-[#d8d4f5] hover:bg-[#d8d4f5]"
            >
              <Icon name="lucide:calendar" class="size-3.5" />
              Add to Calendar
            </a>
          </div>
        </div>

        <div class="mt-0 flex flex-col">
          <EventSession
            time="11.30 am"
            title="Understanding the Choice of Law Dataverse"
          >
            <p>
              Welcome &amp; live demonstration of the platform's main features.
            </p>
            <p><strong>Agatha Brandão</strong></p>
          </EventSession>

          <EventSession
            time="12.00 pm"
            title="Party Autonomy: Sacred Principle or Legal Fiction?"
          >
            <p>
              Debate on the relevance and myths of party autonomy in
              international contracts.
            </p>
            <p>
              <strong>Horatia Muir Watt</strong>
              <EventDot />
              <strong>Béligh Elbalti</strong>
            </p>
            <p>Moderated by <strong>Daniel Girsberger</strong></p>
          </EventSession>

          <EventSession time="1.00 pm" title="CoLD × HCCH">
            <p>
              10 years of the HCCH Principles on Choice of Law in International
              Commercial Contracts — and what lies ahead.
            </p>
            <p><strong>Raquel Peixoto</strong></p>
          </EventSession>

          <EventSession
            time="2.00 pm"
            title="Bilateral Q&amp;A"
            tag="Slots available"
            :special-tag="true"
          >
            <p>
              15-minute private sessions to explore the Dataverse for your
              research, ask questions, or sign up as a specialist. Request by
              <b>20 April</b> at
              <a
                href="mailto:mail@cold.global"
                class="text-cold-purple font-medium no-underline"
                >mail@cold.global</a
              >
            </p>
          </EventSession>

          <EventSession
            time="4.00 pm"
            title="From Promise to Practice: CoLD Assessment"
            tag="Invitation only"
          >
            <p>
              In-person event
              <EventDot />
              Max Chocolatier, Luzern
            </p>
          </EventSession>

          <EventSession
            time="5.00 pm"
            title="Using the Dataverse for Advancing PIL Research"
            :last="true"
          >
            <p>Perspectives on comparative law and case law analysis.</p>
            <p>
              <strong>Rorick Tovar</strong>
              <EventDot />
              <strong>Solomon Okorley</strong>
              <EventDot />
              <strong>Ying Wang</strong>
            </p>
          </EventSession>
        </div>

        <div
          class="border-cold-gray mt-8 flex flex-wrap items-center justify-between gap-4 border-t pt-6 pb-6"
        >
          <div class="text-cold-charcoal text-sm leading-relaxed">
            Join the full event or individual panels<br />
            <a
              href="mailto:mail@cold.global"
              class="text-cold-purple font-medium no-underline"
              >mail@cold.global</a
            >
          </div>
          <div class="flex items-center gap-5">
            <img
              :src="`${ASSET_BASE_URL}/snf-logo.svg`"
              alt="Swiss National Science Foundation"
              class="h-7 w-auto object-contain"
            />
            <img
              src="/images/unilu-logo.svg"
              alt="Universität Luzern"
              class="h-7 w-auto object-contain"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Icon } from "#components";
import { ASSET_BASE_URL } from "@/config/assets";
import EventSession from "@/components/event/EventSession.vue";
import EventDot from "@/components/event/EventDot.vue";

const zoomUrl =
  "https://unilu.zoom.us/j/65808983107?pwd=bqJa2WJOlavMwaDgTY8qZFZbgcSB5T.1";

const calendarUrl =
  "https://calendar.google.com/calendar/render?action=TEMPLATE&text=CoLD%20Launch%20Event%20%E2%80%94%20Choice%20of%20Law%20Dataverse%20in%20Action&dates=20260428T113000%2F20260428T153000&ctz=Europe%2FZurich&details=Join%20via%20Zoom%3A%20https%3A%2F%2Funilu.zoom.us%2Fj%2F65808983107%3Fpwd%3DbqJa2WJOlavMwaDgTY8qZFZbgcSB5T.1%0A%0Acold.global&location=Online%20(Zoom)";

useHead({
  title: "CoLD Launch — 28 April 2026",
});
</script>

<style scoped>
:deep(.text-sm strong) {
  font-weight: 600;
  color: var(--color-cold-night);
  background: linear-gradient(to top, #ebe9f8 40%, transparent 40%);
  padding-inline: 2px;
}
</style>
