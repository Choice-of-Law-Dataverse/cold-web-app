<template>
  <UCard class="cold-ucard flex h-full w-full">
    <div class="flex w-full flex-col gap-4">
      <div>
        <h2 class="popular-title">Leading Cases</h2>
        <p class="result-value-small mb-0">Read top-ranked court decisions</p>
      </div>
      <div v-if="isLoading">
        <LoadingLandingPageCard />
      </div>
      <template v-else>
        <div
          v-for="(decision, index) in leadingCases?.slice(0, 3)"
          :key="index"
        >
          <NuxtLink :to="`/court-decision/${decision.ID}`">
            <UButton class="suggestion-button" variant="link">
              <span
                class="mr-3 inline-flex min-w-[40px] items-center justify-center"
              >
                <img
                  :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${decision['Jurisdictions Alpha-3 Code'].toLowerCase()}.svg`"
                  class="border-cold-gray h-5 border"
                >
              </span>
              <span class="text-left break-words">
                {{
                  decision["Publication Date ISO"]
                    ? formatYear(decision["Publication Date ISO"])
                    : decision["Date"]
                }}:
                {{ decision["Case Title"] }}
              </span>
            </UButton>
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
