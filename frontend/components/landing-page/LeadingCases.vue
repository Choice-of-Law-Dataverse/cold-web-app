<template>
  <UCard class="cold-ucard">
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
                  decision['Publication Date ISO']
                    ? formatYear(decision['Publication Date ISO'])
                    : decision['Date']
                }}:
                {{ decision['Case Title'] }}
              </span>
            </UButton>
          </RouterLink>
        </div>
        <div class="mt-8">
          <ShowMoreLess
            v-if="leadingCases.length > 3"
            :is-expanded="showAll"
            label="leading cases"
            button-class="suggestion-button"
            icon-class="showmoreless-icon-large"
            @update:is-expanded="showAll = $event"
          />
        </div>
      </template>
    </div>
  </UCard>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import LoadingLandingPageCard from '@/components/layout/LoadingLandingPageCard.vue'
import ShowMoreLess from '@/components/ui/ShowMoreLess.vue'
import { useLeadingCases } from '@/composables/useLeadingCases'
import { formatYear } from '@/utils/format'

const showAll = ref(false)

const { data: leadingCases, isLoading } = useLeadingCases()
</script>

<style scoped>
.result-value-small {
  line-height: 36px !important;
  margin-bottom: 0px !important;
}
</style>
