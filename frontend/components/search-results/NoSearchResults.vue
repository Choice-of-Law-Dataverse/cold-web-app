<template>
  <div class="no-results mt-12">
    <h2>Sorry, there are no results for your search.</h2>
  </div>

  <div v-if="jurisdictionFilter && queryContainsJurisdiction">
    <div class="no-results mt-4">
      <h2>
        Maybe try
        <NuxtLink variant="link" @click="removeJurisdictionFilter"
          >removing the jurisdiction</NuxtLink
        >
        from the filter?
      </h2>
    </div>
  </div>

  <div class="no-results mt-4">
    <h2>
      If you think something is wrong, please <a href="/contact">contact us</a>.
    </h2>
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
