<template>
  <div class="no-results mt-12">
    <h2>Sorry, there are no results for your search.</h2>
  </div>

  <div v-if="jurisdictionFilter && queryContainsJurisdiction">
    <div class="no-results mt-4">
      <h2>
        Maybe try
        <UButton
          class="suggestion-button"
          variant="link"
          @click="removeJurisdictionFilter"
        >
          <span>removing {{ jurisdictionFilter }}</span>
        </UButton>
        from the filter?
      </h2>
    </div>
  </div>

  <div class="no-results mt-4">
    <h2>
      Would you like to suggest a court decision, a legal instrument, a
      literature entry, or other information to be included in our
      systematization? Please consider submitting
      <NuxtLink to="/submit" class="suggestion-link">new data</NuxtLink> to help
      us build the Choice of Law Dataverse.
    </h2>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
import { computed } from "vue";
import jurisdictionsData from "@/assets/jurisdictions-data.json";

const route = useRoute();
const router = useRouter();

const jurisdictionFilter = computed(() => {
  return route.query.jurisdiction
    ? String(route.query.jurisdiction).replace(/,/g, ", ")
    : null;
});

const queryContainsJurisdiction = computed(() => {
  const q = (route.query.q || "").toLowerCase();
  if (!q) return false;
  const words = q.split(/\s+/);
  const jurisdictionTerms = jurisdictionsData
    .flatMap((j) => [...(j.name || []), ...(j.alternative || [])])
    .flatMap((term) => term.split(",").map((t) => t.trim().toLowerCase()));
  return words.some((word) => jurisdictionTerms.includes(word));
});

function removeJurisdictionFilter() {
  const newQuery = { ...route.query };
  delete newQuery.jurisdiction;
  router.replace({ path: route.path, query: newQuery });
}
</script>

<style scoped>
.no-results {
  text-align: center;
  font-weight: 600 !important;
}

.suggestion-button {
  font-weight: 600 !important;
}

.suggestion-link {
  color: var(--color-cold-purple);
  text-decoration: underline;
  font-weight: 600 !important;
}

.suggestion-link:hover {
  opacity: 0.8;
}
</style>
