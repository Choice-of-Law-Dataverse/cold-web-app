<template>
  <!-- <UInput
    size="xl"
    icon="i-heroicons-magnifying-glass-20-solid"
    trailing
    v-model="searchText"
    @keyup.enter="performSearch"
    placeholder="Search the entire Dataverse"
    style="width: 40vw"
    class="mr-auto"
  /> -->

  <div class="relative" style="width: 40vw">
    <!-- Input Field -->
    <UInput
      size="xl"
      icon="i-heroicons-magnifying-glass-20-solid"
      trailing
      v-model="searchText"
      @keyup.enter="performSearch"
      placeholder="Search the entire Dataverse"
      style="padding-right: 90px; width: 100%"
      class="mr-auto"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import HelperChatbot from './HelperChatbot.vue' // Import HelperChatbot

// Regular ref for non-persistent search text and results
const searchText = ref('') // Empty string as initial value
const results = ref(null) // Non-persistent search results
const showSuggestions = ref(true) // Add this to control the visibility of the SearchSuggestions component
const loading = ref(false) // Track the loading state
const noResults = ref(false) // Track whether there are no results
const searchPerformed = ref(false) // This will track whether the search was performed

// Update search text when suggestion is clicked
const updateSearchText = (suggestion: string) => {
  searchText.value = suggestion
  showSuggestions.value = false // Hide suggestions when a suggestion is clicked
  performSearch() // Trigger the search after updating the search text
}

// Set up functions to retrieve user data (https://developer.mozilla.org/en-US/docs/Web/API/Navigator)

// Browser Info
const getBrowserInfo = () => {
  const userAgent = navigator.userAgent // User agent string with browser and OS info
  const platform = navigator.platform // Operating system platform
  const language = navigator.language // Browser's language setting
  const screenWidth = window.screen.width // Screen width
  const screenHeight = window.screen.height // Screen height

  return {
    userAgent, // Provides browser and OS information in a single string
    platform, // Provides info about the operating system
    language, // Browser language setting
    screenWidth, // Screen width in pixels
    screenHeight, // Screen height in pixels
  }
}

// User Info
const fetchUserInfo = async () => {
  try {
    // Initial request to get the client hints (https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers#client_hints)
    await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/get_user_info',
      {
        method: 'GET',
      }
    )

    // After getting client hints from the browser, make a second request
    const response = await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/user_info',
      {
        method: 'GET',
      }
    )

    const data = await response.json()
    return data // Return the user info data
  } catch (error) {
    console.error('Error fetching user info:', error)
    return null // Return null if there's an error
  }
}

// Perform Search
const performSearch = async () => {
  showSuggestions.value = false // Hide suggestions when the search button is clicked
  if (searchText.value.trim()) {
    loading.value = true // Set loading to true when search starts
    noResults.value = false // Reset noResults before a new search
    searchPerformed.value = false // Reset before performing the search

    // Get browser and device info
    const browserInfo = getBrowserInfo()

    try {
      // Fetch the user's IP address using an external API
      const ipResponse = await fetch('https://api.ipify.org?format=json')
      const ipData = await ipResponse.json()
      const userIp = ipData.ip

      // Fetch detailed user info (browser, platform, etc.)
      const userInfo = await fetchUserInfo() // Call the fetchUserInfo function and await the result

      const requestBody = {
        search_string: searchText.value,
        time: new Date().toISOString(), // Add timestamp as ISO string
        ip_address: userIp, // Add user's IP address
        browser_info_navigator: browserInfo, // Add browser and device info from navigator
        browser_info_hint: userInfo || {}, // Add user info (platform, version, etc.) from client hint
      }

      const response = await fetch(
        'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/full_text_search',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        }
      )

      const data = await response.json()
      results.value = data

      // Check if total_matches is 0
      if (data.total_matches === 0) {
        noResults.value = true // Display NoSearchResults component
      }
    } catch (error) {
      console.error('Error performing search:', error)
    } finally {
      loading.value = false // Set loading to false when search completes
      await nextTick() // Ensure the DOM updates before setting searchPerformed to true
      searchPerformed.value = true
    }
  }
}
</script>

<!-- <script setup lang="ts">
const searchText = ref('') // Empty string as initial value
const results = ref(null) // Non-persistent search results
const noResults = ref(false) // Track whether there are no results
const loading = ref(false) // Track the loading state

// Browser Info
const getBrowserInfo = () => {
  const userAgent = navigator.userAgent // User agent string with browser and OS info
  const platform = navigator.platform // Operating system platform
  const language = navigator.language // Browser's language setting
  const screenWidth = window.screen.width // Screen width
  const screenHeight = window.screen.height // Screen height

  return {
    userAgent, // Provides browser and OS information in a single string
    platform, // Provides info about the operating system
    language, // Browser language setting
    screenWidth, // Screen width in pixels
    screenHeight, // Screen height in pixels
  }
}

// User Info
const fetchUserInfo = async () => {
  try {
    // Initial request to get the client hints (https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers#client_hints)
    await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/get_user_info',
      {
        method: 'GET',
      }
    )

    // After getting client hints from the browser, make a second request
    const response = await fetch(
      'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/user_info',
      {
        method: 'GET',
      }
    )

    const data = await response.json()
    return data // Return the user info data
  } catch (error) {
    console.error('Error fetching user info:', error)
    return null // Return null if there's an error
  }
}

// Perform Search
const performSearch = async () => {
  //showSuggestions.value = false // Hide suggestions when the search button is clicked
  if (searchText.value.trim()) {
    //loading.value = true // Set loading to true when search starts
    //noResults.value = false // Reset noResults before a new search
    //searchPerformed.value = false // Reset before performing the search

    // Get browser and device info
    const browserInfo = getBrowserInfo()

    try {
      // Fetch the user's IP address using an external API
      const ipResponse = await fetch('https://api.ipify.org?format=json')
      const ipData = await ipResponse.json()
      const userIp = ipData.ip

      // Fetch detailed user info (browser, platform, etc.)
      const userInfo = await fetchUserInfo() // Call the fetchUserInfo function and await the result

      const requestBody = {
        search_string: searchText.value,
        time: new Date().toISOString(), // Add timestamp as ISO string
        ip_address: userIp, // Add user's IP address
        browser_info_navigator: browserInfo, // Add browser and device info from navigator
        browser_info_hint: userInfo || {}, // Add user info (platform, version, etc.) from client hint
      }

      const response = await fetch(
        'https://cold-web-app.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/full_text_search',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        }
      )

      const data = await response.json()
      results.value = data

      // Check if total_matches is 0
      if (data.total_matches === 0) {
        noResults.value = true // Display NoSearchResults component
      }
    } catch (error) {
      console.error('Error performing search:', error)
    } finally {
      //loading.value = false // Set loading to false when search completes
      await nextTick() // Ensure the DOM updates before setting searchPerformed to true
      //searchPerformed.value = true
    }
  }
}
</script> -->
