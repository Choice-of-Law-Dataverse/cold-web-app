<template>
  <div class="bg-cold-bg flex min-h-dvh flex-col">
    <Nav />

    <main class="main-content flex-1 px-3 py-6 sm:px-6 sm:py-12">
      <div class="max-w-container mx-auto w-full">
        <div class="flex flex-col gap-4 sm:gap-6">
          <ErrorBoundary>
            <!-- <NuxtPage :transition="pageTransition" /> -->
            <NuxtPage />
          </ErrorBoundary>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>

<script setup lang="ts">
import Nav from "@/components/layout/Nav.vue";
import Footer from "@/components/layout/Footer.vue";
import ErrorBoundary from "@/components/ui/ErrorBoundary.vue";
// import { useNavigationDirection } from "@/composables/useNavigationDirection";

// const { direction } = useNavigationDirection();

// const pageTransition = computed(() => {
//   // Use direction-aware transitions for better back/forward UX
//   if (direction.value === "back") {
//     return {
//       name: "page-back",
//       mode: "out-in" as const,
//     };
//   }
//   if (direction.value === "forward") {
//     return {
//       name: "page-forward",
//       mode: "out-in" as const,
//     };
//   }
//   // Default transition for initial load or unknown direction
//   return {
//     name: "page",
//     mode: "out-in" as const,
//   };
// });
</script>

<style scoped>
/*
 * Main content min-height calculation:
 * - Ensures stable layout during page transitions (prevents footer jump)
 * - Allows footer to peek above fold, hinting at more content
 *
 * Formula: 100dvh - nav - main-margin - footer-margin
 */
.main-content {
  min-height: calc(100dvh - var(--nav-height) - 10rem);
}
</style>
