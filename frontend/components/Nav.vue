<template>
  <div class="flex items-center border-b border-gray-200 dark:border-gray-800">
    <!-- Web App Name -->
    <div class="font-bold whitespace-nowrap ml-4">Choice of Law Dataverse</div>

    <!-- Horizontal Navigation Links -->
    <UHorizontalNavigation :links="links" class="ml-6" />
  </div>
</template>

<script setup lang="ts">
const route = useRoute()

const links = [
  {
    label: 'Search',
    to: '/',
  },
  // {
  //   label: 'About',
  //   to: '/about'
  // }
]
</script>
