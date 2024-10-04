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
