<template>
  <div class="no-results mt-12">
    <div class="icon-container">
      <UIcon
        name="i-material-symbols:search-off"
        class="no-results-icon"
        size="72"
      />
    </div>
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

  <div class="submit-card mt-8">
    <div class="icon-container">
      <NuxtLink to="/submit">
        <UIcon
          name="i-material-symbols:add-notes"
          class="submit-icon"
          size="72"
        />
      </NuxtLink>
    </div>
    <h2 class="card-title">Enter new Data</h2>
    <p class="card-description">
      Would you like to suggest a court decision, a legal instrument, a
      literature entry, or other information to be included in our
      systematization?
    </p>
    <div class="link-container">
      <NuxtLink to="/submit">
        <UButton class="suggestion-button" variant="link">
          Submit your data
        </UButton>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from "vue-router";
import { computed } from "vue";
import { useJurisdictionLookup } from "@/composables/useJurisdictions";

const route = useRoute();

const { data: jurisdictions, isJurisdictionTerm } = useJurisdictionLookup();

const jurisdictionFilter = computed(() => {
  return route.query.jurisdiction
    ? String(route.query.jurisdiction).replace(/,/g, ", ")
    : null;
});

const queryContainsJurisdiction = computed(() => {
  const q = (route.query.q || "").toLowerCase();
  if (!q || !jurisdictions.value) return false;

  const words = q.split(/\s+/);
  return words.some((word) => isJurisdictionTerm(word));
});

function removeJurisdictionFilter() {
  const newQuery = { ...route.query };
  delete newQuery.jurisdiction;
  navigateTo({ path: route.path, query: newQuery }, { replace: true });
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

.icon-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 32px 0;
}

.no-results-icon {
  color: #9ca3af;
}

.submit-card {
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.submit-icon {
  color: var(--color-cold-green);
  transition: transform 0.2s ease;
}

.submit-icon:hover {
  transform: scale(1.1);
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.card-description {
  font-size: 1rem;
  line-height: 1.6;
  color: #4b5563;
  margin-bottom: 1.5rem;
}

.link-container {
  display: flex;
  justify-content: center;
}
</style>
