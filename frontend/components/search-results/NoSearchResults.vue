<template>
  <div class="no-results result-value-small">
    Sorry, there are no results for your search.<br />
    Do you think this is an error? Please contact us at
    <a href="mailto:mail@cold.global">mail@cold.global</a>.
    <div v-if="jurisdictionFilter && queryContainsJurisdiction">
      <div class="mt-4">
        Maybe you want to remove the jurisdiction from the filter?
      </div>
      <UButton class="mt-2" variant="link" @click="removeJurisdictionFilter">
        Remove Jurisdiction Filter
      </UButton>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import jurisdictionsData from '@/assets/jurisdictions-data.json'

const route = useRoute()
const router = useRouter()

const jurisdictionFilter = computed(() => {
  return route.query.jurisdiction || null
})

const queryContainsJurisdiction = computed(() => {
  const q = (route.query.q || '').toLowerCase()
  if (!q) return false
  const words = q.split(/\s+/)
  // Flatten all names and denonyms from jurisdictionsData
  const jurisdictionTerms = jurisdictionsData
    .flatMap((j) => [...(j.name || []), ...(j.alternative || [])])
    .flatMap((term) => term.split(',').map((t) => t.trim().toLowerCase()))
  // Check if any word in the query matches a jurisdiction term
  return words.some((word) => jurisdictionTerms.includes(word))
})

function removeJurisdictionFilter() {
  const newQuery = { ...route.query }
  delete newQuery.jurisdiction
  router.replace({ path: route.path, query: newQuery })
}
</script>

<style scoped>
.no-results {
  text-align: center;
}
</style>
