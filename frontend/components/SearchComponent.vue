<template>
  <div style="display: flex; flex-direction: column; align-items: center; width: 100%;">
    <!-- Input field and button aligned horizontally -->
    <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 20px;">
      <UInput
        size="xl"
        v-model="searchText"
        @keyup.enter="performSearch"
        placeholder="Enter your search terms here"
        style="width: 40vw;"
      />
      <UButton
      :loading="loading"
      loading-icon="i-material-symbols:progress-activity"
      style="margin-left: 20px; min-width: 82px; display: flex; justify-content: center; align-items: center;"
      size="xl"
      @click="performSearch"
      >
      {{ loading ? '' : 'Search' }}
    </UButton>
    </div>
    
    <!-- Display search suggestions below the input and button -->
    <div>
      <SearchSuggestions v-if="showSuggestions" @suggestion-selected="updateSearchText" />
    </div>

    <!-- Display message that no search results were found -->
    <div v-if="noResults">
      <NoSearchResults />
    </div>

    <!-- Display search results below the input and button -->
    <div v-if="results && !noResults">
      <SearchResults :data="results" />
    </div>

  </div>
</template>

<script setup lang="ts">

// Regular ref for non-persistent search text and results
const searchText = ref('') // Empty string as initial value
const results = ref(null) // Non-persistent search results
const showSuggestions = ref(true); // Add this to control the visibility of the SearchSuggestions component
const loading = ref(false); // Track the loading state
const noResults = ref(false); // Track whether there are no results

// Update search text when suggestion is clicked
const updateSearchText = (suggestion: string) => {
  searchText.value = suggestion;
  showSuggestions.value = false; // Hide suggestions when a suggestion is clicked
  performSearch(); // Trigger the search after updating the search text
}

const getBrowserInfo = () => {
  const userAgent = navigator.userAgent; // User agent string with browser and OS info
  const platform = navigator.platform; // Operating system platform
  const language = navigator.language; // Browser's language setting
  const screenWidth = window.screen.width; // Screen width
  const screenHeight = window.screen.height; // Screen height

  return {
    userAgent, // Provides browser and OS information in a single string
    platform, // Provides info about the operating system
    language, // Browser language setting
    screenWidth, // Screen width in pixels
    screenHeight, // Screen height in pixels
  };
};

const performSearch = async () => {
  showSuggestions.value = false; // Hide suggestions when the search button is clicked
  if (searchText.value.trim()) {
    loading.value = true; // Set loading to true when search starts
    noResults.value = false; // Reset noResults before a new search

    // Get browser and device info
    const browserInfo = getBrowserInfo();

    try {
      // Fetch the user's IP address using an external API
      const ipResponse = await fetch('https://api.ipify.org?format=json');
      const ipData = await ipResponse.json();
      const userIp = ipData.ip;

    const requestBody = {
      search_string: searchText.value,
      time: new Date().toISOString(), // Add timestamp as ISO string
      ip_address: userIp, // Add user's IP address
      browser_info: browserInfo, // Add browser and device info
    };

    // Print the request body to the console for testing purposes
    console.log(JSON.stringify(requestBody));

    const response = await fetch('https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/curated_search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });
    
    const data = await response.json();
    results.value = data;

    // Check if total_matches is 0
    if (data.total_matches === 0) {
      noResults.value = true; // Display NoSearchResults component
    }

    } catch (error) {
      console.error('Error performing search:', error);
    } finally {
      loading.value = false; // Set loading to false when search completes
    }
  }
}

</script>
