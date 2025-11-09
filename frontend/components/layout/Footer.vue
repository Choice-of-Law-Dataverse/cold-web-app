<script setup>
import { aboutNavLinks, learnNavLinks } from "@/config/pageConfigs.js";
</script>

<template>
  <footer class="mt-24 min-h-[300px] bg-cold-night px-6 py-12 text-white">
    <div class="mx-auto max-w-container">
      <!-- Logo and Tagline -->
      <div class="mb-8 flex flex-col gap-3">
        <img
          src="https://choiceoflaw.blob.core.windows.net/assets/cold_flag_footer.svg"
          class="w-25 mb-6 max-w-16"
        >
        <h2 class="!font-bold leading-tight">Choice of Law<br >Dataverse</h2>
        <p class="leading-snug">
          Funded by the<br >Swiss National Science Foundation
        </p>
      </div>

      <!-- Footer Sitemap - 3 Columns -->
      <div
        class="grid grid-cols-1 gap-8 border-t border-gray-700 pt-8 md:grid-cols-3"
      >
        <!-- Column 1: About with subpages -->
        <div class="flex flex-row justify-between gap-3 md:flex-col">
          <h3 class="mb-2 font-bold">About</h3>
          <div class="flex flex-col gap-3 text-right md:text-left">
            <NuxtLink
              v-for="link in aboutNavLinks"
              :key="link.key"
              :to="link.path"
              class="text-sm !text-white hover:underline"
            >
              {{ link.label }}
            </NuxtLink>
          </div>
        </div>

        <!-- Column 2: Learn with subpages -->
        <div class="flex flex-row justify-between gap-3 md:flex-col">
          <h3 class="mb-2 font-bold">Learn</h3>
          <div class="flex flex-col gap-3 text-right md:text-left">
            <NuxtLink
              v-for="link in learnNavLinks"
              :key="link.key"
              :to="link.path"
              class="text-sm !text-white hover:underline"
            >
              {{ link.label }}
            </NuxtLink>
          </div>
        </div>

        <!-- Column 3: Utilities -->
        <div
          class="flex flex-row justify-between gap-3 md:flex-col md:justify-start"
        >
          <h3 class="mb-2 font-bold">Resources</h3>
          <div class="flex flex-col gap-3 text-right md:text-left">
            <NuxtLink to="/contact" class="text-sm !text-white hover:underline">
              Contact
            </NuxtLink>
            <NuxtLink to="/search" class="text-sm !text-white hover:underline">
              Search
            </NuxtLink>
            <NuxtLink
              to="/disclaimer"
              class="text-sm !text-white hover:underline"
            >
              Disclaimer
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
a {
  font-weight: 600 !important;
}

h2 {
  color: white !important;
}

h3 {
  color: white !important;
  font-size: 1rem;
}
</style>
