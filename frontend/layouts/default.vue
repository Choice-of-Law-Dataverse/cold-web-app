<template>
  <div class="flex min-h-screen flex-col bg-cold-bg">
    <Nav />

    <main class="mt-12 flex-1 px-6">
      <div class="flex flex-col gap-6">
        <ErrorBoundary>
          <NuxtPage />
        </ErrorBoundary>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup>
import Nav from "@/components/layout/Nav.vue";
import Footer from "@/components/layout/Footer.vue";
import ErrorBoundary from "@/components/ui/ErrorBoundary.vue";
</script>
