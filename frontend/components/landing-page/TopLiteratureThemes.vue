<template>
  <UCard class="cold-ucard">
    <div class="popular-searches-container flex flex-col gap-8">
      <!-- Title Section -->
      <div>
        <h2 class="popular-title text-left md:whitespace-nowrap">
          Top Literature Themes
        </h2>
      </div>

      <!-- Suggestions Section -->
      <div class="suggestions flex flex-wrap gap-6">
        <UButton
          v-for="(suggestion, index) in searchSuggestions"
          :key="index"
          @click="handleSuggestionClick(suggestion)"
          class="suggestion-button"
          variant="link"
          icon="i-material-symbols:arrow-forward"
          trailing
        >
          <span class="break-words text-left">{{ suggestion }}</span>
        </UButton>
      </div>
    </div>
  </UCard>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import eventBus from '@/eventBus'

const router = useRouter()

const searchSuggestions = ref(['Arbitration', 'Rules of law', 'Tacit choice'])

function formatQuery(query) {
  return query.replace(/ /g, '+')
}

function handleSuggestionClick(suggestion) {
  // Pass the query with both theme and type=Literature
  router.push({
    name: 'search',
    query: { theme: suggestion, type: 'Literature' },
  })
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
