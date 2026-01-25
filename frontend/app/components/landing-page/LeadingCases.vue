<template>
  <UCard
    class="cold-ucard landing-card flex h-full w-full overflow-hidden"
    :ui="{ body: '!p-0' }"
  >
    <div class="gradient-top-border" />
    <div class="flex w-full flex-col gap-4 p-4 sm:p-6">
      <div>
        <h2 class="card-title">Leading Cases</h2>
        <p class="card-subtitle mb-0">Read top-ranked court decisions</p>
      </div>
      <div v-if="isLoading">
        <LoadingLandingPageCard />
      </div>
      <InlineError v-else-if="error" :error="error" />
      <template v-else-if="leadingCases">
        <div class="flex w-full flex-col gap-2">
          <NuxtLink
            v-for="(decision, index) in leadingCases.slice(0, 3)"
            :key="index"
            :to="`/court-decision/${decision.ID}`"
            class="landing-item-button type-court-decision w-full"
          >
            <div class="flag-wrapper">
              <CountryFlag
                :iso3="decision['Jurisdictions Alpha-3 Code']"
                class="item-flag"
              />
            </div>
            <span class="item-title">
              {{ decision["Case Title"] }}
            </span>
            <span class="item-year">
              {{
                decision["Publication Date ISO"]
                  ? formatYear(decision["Publication Date ISO"])
                  : decision["Date"]
              }}
            </span>
          </NuxtLink>
        </div>
      </template>
    </div>
  </UCard>
</template>

<script setup>
import LoadingLandingPageCard from "@/components/layout/LoadingLandingPageCard.vue";
import InlineError from "@/components/ui/InlineError.vue";
import CountryFlag from "@/components/ui/CountryFlag.vue";
import { useLeadingCases } from "@/composables/useFullTable";
import { formatYear } from "@/utils/format";

const { data: leadingCases, isLoading, error } = useLeadingCases();
</script>
