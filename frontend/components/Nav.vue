<template>
  <div class="flex items-center border-b border-gray-200 dark:border-gray-800">
    <!-- Web App Name -->
    <div class="font-bold whitespace-nowrap ml-4"><a href="/">CoLD</a></div>

    <!-- Search Input -->
    <UInput
      size="xl"
      v-model="searchText"
      placeholder="Enter your search terms here"
      style="width: 40vw"
    />
    <UButton @click="emitSearch">Search</UButton>
    <!-- <UInput
      size="xl"
      v-model="searchText"
      @keyup.enter="performSearch"
      placeholder="Search the entire Dataverse"
      style="width: 40vw"
      class="mr-auto"
    /> -->

    <!-- Horizontal Navigation Links -->
    <UHorizontalNavigation :links="links" class="ml-6" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// const route = useRoute()
const searchText = ref('') // Define searchText to bind to the input
const router = useRouter() // Router instance to handle navigation

const links = [
  // {
  //   label: 'CoLD',
  //   to: '/',
  // },
  {
    label: 'About',
    to: '/about',
  },
  {
    label: 'Contact',
    to: '/contact',
  },
]

function emitSearch() {
  if (searchText.value.trim()) {
    // Only navigate if there's a non-empty search term
    router.push({ name: 'search', query: { q: searchText.value } })
  }
}
</script>
