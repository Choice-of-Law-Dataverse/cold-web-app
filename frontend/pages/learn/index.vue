<template>
  <div ></div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// Initialize router and route
const router = useRouter()
const route = useRoute()

// Redirect to OpenEducationalResources if we're on the base learn page
onMounted(() => {
  if (route.path === '/learn') {
    router.replace('/learn/open-educational-resources')
  }
})
</script>

<style scoped>
.main-conten {
  max-width: var(--container-width);
  margin: 0 auto;
  width: 100%;
}
</style>
