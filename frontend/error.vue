<template>
  <div class="bg-cold-bg min-h-screen flex flex-col">
    <!-- Navigation Bar -->
    <Nav />

    <!-- Main Content Area -->
    <main class="flex-1 mt-12 px-6">
      <div
        class="mx-auto min-h-[50vh] flex flex-col justify-center items-center text-center"
        style="max-width: var(--container-width); width: 100%"
      >
        <h2>{{ errorMessage }}</h2>

        <NuxtLink to="/" class="mt-6"> Back to Home </NuxtLink>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Nav from '~/components/layout/Nav.vue'
import Footer from '~/components/layout/Footer.vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const errorMessage = route.query.message || 'An error occurred'
</script>
