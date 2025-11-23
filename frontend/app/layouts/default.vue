<template>
  <div class="bg-cold-bg flex min-h-screen flex-col">
    <Nav />

    <main class="mt-12 flex-1 px-6">
      <div class="max-w-container mx-auto w-full">
        <div class="flex flex-col gap-6">
          <ErrorBoundary>
            <NuxtPage />
          </ErrorBoundary>
        </div>
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
