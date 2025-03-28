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
        <h2 class="text-3xl font-bold mb-4">{{ error.statusCode }} Error</h2>
        <p class="text-lg text-gray-600">{{ error.message }}</p>

        <NuxtLink to="/" class="mt-6 text-blue-500 hover:underline">
          Back to home
        </NuxtLink>
      </div>
    </main>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import Nav from '~/components/Nav.vue'
import Footer from '~/components/Footer.vue'

defineProps(['error'])
</script>
