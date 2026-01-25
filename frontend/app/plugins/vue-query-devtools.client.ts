import { VueQueryDevtools } from "@tanstack/vue-query-devtools";
import { defineNuxtPlugin } from "#app";

export default defineNuxtPlugin((nuxtApp) => {
  if (process.env.NODE_ENV === "development") {
    nuxtApp.vueApp.component("VueQueryDevtools", VueQueryDevtools);
  }
});
