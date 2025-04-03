<template>
  <div></div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// Initialize router and route
const router = useRouter()
const route = useRoute()

// Redirect to about-cold if we're on the base about page
onMounted(() => {
  if (route.path === '/about') {
    router.replace('/about/about-cold')
  }
})
</script>

<style scoped>
.main-content {
  max-width: var(--container-width);
  margin: 0 auto;
  width: 100%;
}
</style>
