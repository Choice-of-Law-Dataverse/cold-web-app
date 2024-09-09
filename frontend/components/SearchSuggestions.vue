<template>
    <div>
        <h3>Search Suggestions:</h3>
      <div class="suggestions-container">
        <div v-for="(suggestion, index) in searchSuggestions" :key="index" class="suggestion-button">
          <UButton
            color="primary"
            variant="soft"
            size="lg"
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
        searchSuggestions: ["Search Suggestion 1", "Search Suggestion 2", "Search Suggestion 3"]
      };
    }
  };
  </script>
  
  <style scoped>

h3 {
    font-size: medium;
    margin-bottom: 1em;
    margin-top: 1em;
    text-align: center; /* Center the text */
  }

  .suggestions-container {
    display: flex;
    gap: 10px; /* Adds space between buttons */
  }
  
  .suggestion-button {
    flex-shrink: 0; /* Prevents the buttons from shrinking */
  }
  </style>
  