<template>
  <UCard class="cold-ucard flex h-full w-full flex-col">
    <h2 class="popular-title">Leading Cases</h2>
    <p class="result-value-small">Court decisions ranked highly in CoLD</p>
    <div>
      <div v-if="isLoading">
        <LoadingLandingPageCard />
      </div>
      <template v-else>
        <div
          v-for="(decision, index) in leadingCases?.slice(0, 3)"
          :key="index"
        >
          <RouterLink :to="`/court-decision/${decision.ID}`">
            <UButton class="suggestion-button mt-8" variant="link">
              <img
                :src="`https://choiceoflaw.blob.core.windows.net/assets/flags/${decision['Jurisdictions Alpha-3 Code'].toLowerCase()}.svg`"
                class="mr-3 h-5 border border-cold-gray"
              >
              <span class="break-words text-left">
                {{
                  decision["Publication Date ISO"]
                    ? formatYear(decision["Publication Date ISO"])
                    : decision["Date"]
                }}:
                {{ decision["Case Title"] }}
              </span>
            </UButton>
          </RouterLink>
        </div>
      </template>
    </div>
  </UCard>
</template>

<script setup>
import { RouterLink } from "vue-router";
import LoadingLandingPageCard from "@/components/layout/LoadingLandingPageCard.vue";
import { useLeadingCases } from "@/composables/useLeadingCases";
import { formatYear } from "@/utils/format";

const { data: leadingCases, isLoading } = useLeadingCases();
</script>

<style scoped>
.result-value-small {
  line-height: 36px !important;
  margin-bottom: 0px !important;
}
</style>
