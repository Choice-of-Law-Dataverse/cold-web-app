<template>
  <div class="bg-cold-bg flex min-h-screen flex-col">
    <Nav />

    <main class="mt-12 flex-1 px-6">
      <div
        class="max-w-container mx-auto flex min-h-[50vh] w-full flex-col items-center justify-center text-center"
      >
        <h2>{{ errorMessage }}</h2>

        <NuxtLink to="/" class="text-cold-teal mt-6">
          Take me back to Home
        </NuxtLink>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Nav from "@/components/layout/Nav.vue";
import Footer from "@/components/layout/Footer.vue";
import { useRoute } from "vue-router";

const route = useRoute();
const errorMessage =
  route.query.message || "Sorry, we can’t find the page you’re looking for.";
</script>
