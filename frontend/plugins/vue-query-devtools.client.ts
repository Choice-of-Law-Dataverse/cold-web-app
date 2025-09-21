import { VueQueryDevtools } from "@tanstack/vue-query-devtools";
import { defineNuxtPlugin } from "#app";

export default defineNuxtPlugin((nuxtApp) => {
  // Only enable devtools in development
  if (process.env.NODE_ENV === "development") {
    // Register the devtools component globally
    nuxtApp.vueApp.component("VueQueryDevtools", VueQueryDevtools);
  }
});
