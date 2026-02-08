<script setup lang="ts">
import { aboutNavLinks, learnNavLinks } from "@/config/navigation";

const user = useUser();
</script>

<template>
  <footer
    class="footer-container min-h-[300px] px-6 pt-6 pb-24 sm:pt-12 md:pb-12"
  >
    <div class="max-w-container mx-auto">
      <!-- Logo and Tagline - horizontal on desktop, stacked on mobile -->
      <div
        class="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <!-- Left: Flag + Title -->
        <div class="flex items-center gap-4">
          <img
            src="https://choiceoflaw.blob.core.windows.net/assets/cold_flag_footer.svg"
            class="h-12 w-auto sm:h-14"
            alt="Choice of Law Dataverse flag"
          />
          <h2 class="footer-title leading-tight text-pretty">
            Choice of Law Dataverse
          </h2>
        </div>

        <!-- Right: Funding attribution -->
        <p class="leading-snug text-pretty text-gray-300 sm:text-right">
          Funded by the Swiss National Science Foundation
        </p>
      </div>

      <!-- Footer Sitemap - 3 Columns -->
      <div class="footer-border grid grid-cols-1 gap-8 pt-8 md:grid-cols-3">
        <!-- Column 1: About with subpages -->
        <div class="flex flex-row justify-between gap-3 md:flex-col">
          <h3 class="footer-heading mb-2">About</h3>
          <div class="flex flex-col gap-3 text-right md:text-left">
            <NuxtLink
              v-for="link in aboutNavLinks"
              :key="link.key"
              :to="link.path"
              class="footer-link"
            >
              {{ link.label }}
            </NuxtLink>
          </div>
        </div>

        <!-- Column 2: Learn with subpages -->
        <div class="flex flex-row justify-between gap-3 md:flex-col">
          <h3 class="footer-heading mb-2">Learn</h3>
          <div class="flex flex-col gap-3 text-right md:text-left">
            <NuxtLink
              v-for="link in learnNavLinks"
              :key="link.key"
              :to="link.path"
              class="footer-link"
            >
              {{ link.label }}
            </NuxtLink>
          </div>
        </div>

        <!-- Column 3: Utilities -->
        <div
          class="flex flex-row justify-between gap-3 md:flex-col md:justify-start"
        >
          <h3 class="footer-heading mb-2">Resources</h3>
          <div class="flex flex-col gap-3 text-right md:text-left">
            <NuxtLink to="/contact" class="footer-link"> Contact </NuxtLink>
            <NuxtLink to="/search" class="footer-link"> Search </NuxtLink>
            <NuxtLink to="/disclaimer" class="footer-link">
              Disclaimer
            </NuxtLink>
          </div>
        </div>
        <div
          class="flex flex-row justify-between gap-3 md:flex-col md:justify-start"
        >
          <h3 class="footer-heading my-2">Admin</h3>
          <div class="flex flex-col gap-3 text-right md:text-left">
            <a
              v-if="user"
              href="/auth/logout"
              class="footer-link cursor-pointer"
            >
              Logout
            </a>

            <a v-else href="/auth/login" class="footer-link cursor-pointer">
              Login
            </a>

            <NuxtLink to="/moderation" class="footer-link">
              Moderation
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>
