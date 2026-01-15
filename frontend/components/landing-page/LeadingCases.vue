<template>
  <UCard class="cold-ucard gradient-top-border landing-card flex h-full w-full">
    <div class="flex w-full flex-col gap-4">
      <div>
        <h2 class="card-title">Leading Cases</h2>
        <p class="card-subtitle mb-0">Read top-ranked court decisions</p>
      </div>
      <div v-if="isLoading">
        <LoadingLandingPageCard />
      </div>
      <template v-else>
        <div class="flex flex-col gap-2">
          <NuxtLink
            v-for="(decision, index) in leadingCases?.slice(0, 3)"
            :key="index"
            :to="`/court-decision/${decision.ID}`"
            class="landing-item-button"
          >
            <div class="flag-wrapper">
              <img
                :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${decision['Jurisdictions Alpha-3 Code'].toLowerCase()}.svg`"
                class="item-flag"
              />
            </div>
            <span class="break-words text-left">
              {{
                decision["Publication Date ISO"]
                  ? formatYear(decision["Publication Date ISO"])
                  : decision["Date"]
              }}:
              {{ decision["Case Title"] }}
            </span>
          </NuxtLink>
        </div>
      </template>
    </div>
  </UCard>
</template>

<script setup>
import LoadingLandingPageCard from "@/components/layout/LoadingLandingPageCard.vue";

import { useLeadingCases } from "@/composables/useLeadingCases";
import { formatYear } from "@/utils/format";

const { data: leadingCases, isLoading } = useLeadingCases();
</script>
