<template>
  <div>
    <div class="mb-12 text-center">
      <h1 class="text-cold-purple mb-4 text-4xl font-bold">Submit New Data</h1>
      <p class="text-cold-night-alpha mx-auto max-w-3xl text-lg">
        Choose the type of data you want to submit to the Choice of Law
        Dataverse. Your contributions help build the most comprehensive resource
        for private international law.
      </p>
    </div>

    <GridContainer class="mx-auto max-w-6xl gap-y-6">
      <GridItem :cols="6" :md-cols="4">
        <ConnectCard
          title="Court Decision"
          subtitle="Submit judicial decisions and case law"
          button-text="Add Court Decision"
          button-link="/court-decision/new"
          icon-name="i-material-symbols:gavel"
          :new-tab="false"
        />
      </GridItem>

      <GridItem :cols="6" :md-cols="4">
        <ConnectCard
          title="Domestic Instrument"
          subtitle="Add national laws and regulations"
          button-text="Add Domestic Instrument"
          button-link="/domestic-instrument/new"
          icon-name="i-material-symbols:account-balance"
          :new-tab="false"
        />
      </GridItem>

      <GridItem :cols="6" :md-cols="4">
        <ConnectCard
          title="Regional Instrument"
          subtitle="Submit regional treaties and agreements"
          button-text="Add Regional Instrument"
          button-link="/regional-instrument/new"
          icon-name="i-material-symbols:public"
          :new-tab="false"
        />
      </GridItem>

      <GridItem :cols="6" :md-cols="4">
        <ConnectCard
          title="International Instrument"
          subtitle="Add international treaties and conventions"
          button-text="Add International Instrument"
          button-link="/international-instrument/new"
          icon-name="i-material-symbols:language"
          :new-tab="false"
        />
      </GridItem>

      <GridItem :cols="6" :md-cols="4">
        <ConnectCard
          title="Literature"
          subtitle="Submit academic articles and publications"
          button-text="Add Literature"
          button-link="/literature/new"
          icon-name="i-material-symbols:menu-book"
          :new-tab="false"
        />
      </GridItem>

      <GridItem :cols="6" :md-cols="4">
        <ConnectCard
          title="Need Help?"
          subtitle="Questions about data submission?"
          button-text="Contact Us"
          button-link="/contact"
          icon-name="i-material-symbols:help-outline"
          :new-tab="false"
        />
      </GridItem>
    </GridContainer>

    <div class="mt-12 text-center">
      <p class="text-cold-night-alpha mx-auto max-w-2xl text-sm">
        Please ensure you have the necessary rights and permissions before
        submitting any content. All submissions are subject to review and may be
        edited for clarity and consistency.
      </p>
    </div>
  </div>
</template>

<script setup>
import { useHead } from "#imports";
import ConnectCard from "@/components/landing-page/ConnectCard.vue";
import GridContainer from "@/components/layout/GridContainer.vue";
import GridItem from "@/components/layout/GridItem.vue";

useHead({
  title: "Submit New Data — CoLD",
  meta: [
    {
      name: "description",
      content:
        "Submit new data to the Choice of Law Dataverse. Add court decisions, legal instruments, and academic literature to help build the most comprehensive private international law resource.",
    },
  ],
});
</script>

<style scoped>
/* Ensure cards have consistent height */
:deep(.cold-ucard) {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
</style>
