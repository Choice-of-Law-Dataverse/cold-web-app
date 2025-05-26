<template>
  <div class="no-results result-value-small">
    Sorry, there are no results for your search.<br />
    Do you think this is an error? Please contact us at
    <a href="mailto:mail@cold.global">mail@cold.global</a>.
    <div v-if="jurisdictionFilter">
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

const route = useRoute()
const router = useRouter()

const jurisdictionFilter = computed(() => {
  // Check if the URL or query contains a jurisdiction filter
  return route.query.jurisdiction || null
})

function removeJurisdictionFilter() {
  // Remove the jurisdiction param from the query and update the URL
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
