<script setup lang="ts">
const route = useRoute()

const links = [{
  label: 'CoLD Search',
  to: '/'
}, {
  label: 'Jurisdiction Comparison'
}, {
  label: 'About',
  to: '/about'
}]
</script>

<template>
  <UHorizontalNavigation :links="links" class="border-b border-gray-200 dark:border-gray-800" />
</template>
