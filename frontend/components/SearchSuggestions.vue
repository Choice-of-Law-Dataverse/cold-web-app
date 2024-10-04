<template>
  <div>
    <h3>Not sure what to search for? Try these searches:</h3>
    <div class="suggestions-container">
      <div
        v-for="(suggestion, index) in searchSuggestions"
        :key="index"
        class="suggestion-button"
      >
        <UButton
          color="gray"
          variant="solid"
          size="lg"
          @click="sendSuggestion(suggestion)"
        >
          {{ suggestion }}
        </UButton>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      searchSuggestions: [
        'Tacit Choice in Argentina',
        'Party Autonomy in Switzerland',
        'Public Policy Definition',
      ],
    }
  },
  methods: {
    sendSuggestion(suggestion) {
      this.$emit('suggestion-selected', suggestion)
    },
  },
}
</script>

<style scoped>
h3 {
  font-size: medium;
  margin-bottom: 1em;
  margin-top: 1.5em;
  text-align: center;
}

.suggestions-container {
  display: flex;
  gap: 20px; /* Adds space between buttons */
}

.suggestion-button {
  flex-shrink: 0; /* Prevents the buttons from shrinking */
}
</style>
