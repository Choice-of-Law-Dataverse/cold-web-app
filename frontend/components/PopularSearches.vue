<template>
  <UCard class="cold-ucard">
    <!-- <div class="popular-searches-container"> -->
    <div class="container mx-auto px-6 flex flex-col items-center relative">
      <h2 class="popular-title">Popular Searches</h2>
      <div class="suggestions">
        <UButton
          v-for="(suggestion, index) in searchSuggestions"
          :key="index"
          @click="handleSuggestionClick(suggestion)"
          class="suggestion-button"
          variant="link"
          icon="i-material-symbols:arrow-forward"
          trailing
        >
          {{ suggestion }}
        </UButton>
      </div>
    </div>
  </UCard>
</template>

<script>
import eventBus from '@/eventBus'

export default {
  data() {
    return {
      searchSuggestions: [
        'Tacit Choice in Argentina',
        'Party Autonomy in Switzerland',
      ],
    }
  },
  methods: {
    formatQuery(query) {
      return query.replace(/ /g, '+')
    },
    handleSuggestionClick(suggestion) {
      // Emit an event to update the search input
      eventBus.emit('update-search', suggestion)

      // Pass the query directly with spaces
      this.$router.push({
        name: 'search',
        query: { q: suggestion }, // Pass suggestion directly without replacing spaces
      })
    },
  },
}
</script>

<style scoped>
.popular-searches-container {
  display: flex;
  align-items: center;
  gap: 48px; /* Space between items */
}

.popular-title {
  white-space: nowrap; /* Prevents the title from wrapping to a new line */
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 36px; /* Space between each suggestion link */
}
</style>
