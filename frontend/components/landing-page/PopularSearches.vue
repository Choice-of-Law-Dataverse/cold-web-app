<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container flex flex-col gap-8">
      <!-- Title Section -->
      <div>
        <h2 class="popular-title text-left md:whitespace-nowrap">
          Popular Searches
        </h2>
      </div>

      <!-- Suggestions Section -->
      <div class="suggestions flex flex-wrap gap-6">
        <UButton
          v-for="(suggestion, index) in searchSuggestions"
          :key="index"
          class="suggestion-button"
          variant="link"
          icon="i-material-symbols:arrow-forward"
          trailing
          @click="handleSuggestionClick(suggestion)"
        >
          <span class="break-words text-left">{{ suggestion }}</span>
        </UButton>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";
import eventBus from "@/eventBus";

const router = useRouter();

const searchSuggestions = ref([
  "Tacit Choice in Argentina",
  "Party Autonomy in Switzerland",
]);

function _formatQuery(query) {
  return query.replace(/ /g, "+");
}

function handleSuggestionClick(suggestion) {
  // Emit an event to update the search input
  eventBus.emit("update-search", suggestion);

  // Pass the query directly with spaces
  router.push({
    name: "search",
    query: { q: suggestion },
  });
}
</script>

<style scoped>
.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem; /* Adjust spacing between buttons */
}

.suggestion-button {
  max-width: 100%; /* Ensure the button doesn’t overflow */
  white-space: normal; /* Allow text wrapping */
  text-align: left; /* Align text to the left */
  padding: 0.5rem 1rem; /* Adjust padding for better fit */
  word-break: break-word; /* Break long words */
}
</style>
